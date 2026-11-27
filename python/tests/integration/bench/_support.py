#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
"""Support code for the configurable Kyuubi benchmark."""

from __future__ import annotations

import argparse
import json
import logging
import math
import statistics
import time
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SQL_DIR = Path(__file__).parents[1] / "resources" / "sql"
ALL_QUERIES = tuple(range(1, 23))
TABLES = (
    "customer",
    "orders",
    "lineitem",
    "part",
    "partsupp",
    "supplier",
    "nation",
    "region",
)
# Rows per unit of scale factor. lineitem is generated, so its count is only
# approximately linear in the scale factor.
BASE_ROW_COUNTS = {
    "customer": 150_000,
    "orders": 1_500_000,
    "lineitem": 6_000_000,
    "part": 200_000,
    "partsupp": 800_000,
    "supplier": 10_000,
}
FIXED_ROW_COUNTS = {"nation": 25, "region": 5}
LINEITEM_TOLERANCE = 0.01
POLL_INTERVAL_SECONDS = 0.05

ENGINE_LABEL = "bench-run"


def parse_query_list(value: str) -> list[int]:
    """Parse a comma-separated list of TPC-H query numbers (argparse type)."""
    if not value.strip():
        return []
    try:
        queries = sorted({int(item) for item in value.split(",")})
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"'{value}' is not a comma-separated list of integers"
        ) from e
    invalid = [q for q in queries if q not in ALL_QUERIES]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"Query numbers must be between 1 and 22, got {invalid}"
        )
    return queries


def parse_spark_conf(value: str) -> tuple[str, str]:
    """Parse a KEY=VALUE Spark configuration entry (argparse type)."""
    key, sep, val = value.partition("=")
    if not sep or not key.strip():
        raise argparse.ArgumentTypeError(f"'{value}' is not in KEY=VALUE format")
    return key.strip(), val.strip()


def execute_with_timeout(cursor, statement: str, timeout: float) -> None:
    """Execute a statement and fetch its results, cancelling it after `timeout` s.

    Kyuubi's server-side query timeout only caps a client-side timeout, which Impyla
    does not offer, so the deadline is enforced here by polling the operation. The
    server holds each status request open for up to 5 s (long polling), so a query
    can overrun the timeout by that much before being cancelled.
    """
    deadline = time.monotonic() + timeout
    cursor.execute_async(statement)
    while cursor.is_executing():
        if time.monotonic() > deadline:
            cursor.cancel_operation()
            raise TimeoutError(f"Query exceeded the {timeout:g}s timeout")
        time.sleep(POLL_INTERVAL_SECONDS)
    cursor.fetchall()


def load_query(number: int) -> str:
    """Read the SQL of a TPC-H query."""
    return (SQL_DIR / f"{number}.sql").read_text()


def scale_factor_number(sf: str) -> int:
    """Convert 'sf10' to 10."""
    return int(sf.removeprefix("sf"))


def expected_row_count(table: str, sf: str) -> int:
    """Expected number of rows of a TPC-H table at a scale factor."""
    if table in FIXED_ROW_COUNTS:
        return FIXED_ROW_COUNTS[table]
    return BASE_ROW_COUNTS[table] * scale_factor_number(sf)


def row_count_is_valid(table: str, sf: str, actual: int) -> bool:
    """Check a table's row count against the expectation for its scale factor."""
    expected = expected_row_count(table, sf)
    if table == "lineitem":
        return abs(actual - expected) <= expected * LINEITEM_TOLERANCE
    return actual == expected


def compute_stats(samples: list[float], failures: int) -> dict[str, Any]:
    """Statistical summary of the successful samples of one query."""
    n = len(samples)
    stats: dict[str, Any] = {
        "n": n,
        "failures": failures,
        "min": None,
        "max": None,
        "avg": None,
        "std": None,
        "median": None,
        "p95": None,
        "cv": None,
    }
    if not n:
        return stats
    avg = statistics.fmean(samples)
    std = statistics.stdev(samples) if n > 1 else None
    stats.update(
        min=min(samples),
        max=max(samples),
        avg=avg,
        std=std,
        median=statistics.median(samples),
        p95=percentile(samples, 95),
        cv=(std / avg) if std is not None and avg else None,
    )
    return stats


def percentile(samples: list[float], pct: float) -> float:
    """Percentile with linear interpolation between closest ranks."""
    ordered = sorted(samples)
    rank = (len(ordered) - 1) * pct / 100
    low, high = math.floor(rank), math.ceil(rank)
    return ordered[low] + (ordered[high] - ordered[low]) * (rank - low)


@dataclass
class BenchmarkResults:
    """Everything recorded during one benchmark invocation."""

    configuration: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    dataset: dict[str, Any] = field(default_factory=dict)
    # query number -> list of {"round", "warmup", "seconds", "error"}
    samples: dict[int, list[dict[str, Any]]] = field(default_factory=dict)
    logs: dict[str, Any] = field(default_factory=dict)
    started: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    finished: str | None = None
    phase: str = "not-started"
    errors: list[str] = field(default_factory=list)

    def record(
        self,
        query: int,
        round_: int,
        warmup: bool,
        seconds: float | None,
        error: str | None,
    ) -> None:
        self.samples.setdefault(query, []).append(
            {"round": round_, "warmup": warmup, "seconds": seconds, "error": error}
        )

    def query_stats(self) -> dict[int, dict[str, Any]]:
        """Per-query statistics, computed over successful timed samples only."""
        result = {}
        for query, samples in sorted(self.samples.items()):
            timed = [s for s in samples if not s["warmup"]]
            ok = [s["seconds"] for s in timed if s["error"] is None]
            result[query] = compute_stats(ok, len(timed) - len(ok))
        return result

    @property
    def total_failures(self) -> int:
        return sum(s["failures"] for s in self.query_stats().values())

    @property
    def complete(self) -> bool:
        """A run is complete if every selected query ran all rounds without error."""
        if self.phase != "finished" or self.errors:
            return False
        runs = self.configuration.get("runs", 0)
        selected = self.configuration.get("queries", [])
        stats = self.query_stats()
        warmup_failures = any(
            x["error"] for q in self.samples.values() for x in q if x["warmup"]
        )
        return not warmup_failures and self.total_failures == 0 and all(
            stats.get(q, {}).get("n") == runs for q in selected
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "complete" if self.complete else "incomplete",
            "phase": self.phase,
            "started": self.started,
            "finished": self.finished,
            "errors": self.errors,
            "configuration": self.configuration,
            "environment": self.environment,
            "dataset": self.dataset,
            "statistics": {str(q): s for q, s in self.query_stats().items()},
            "samples": {str(q): s for q, s in sorted(self.samples.items())},
            "logs": self.logs,
        }


def write_results(results: BenchmarkResults, output_dir: Path) -> None:
    """Write results.json and report.html to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results.finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output_dir / "results.json").write_text(
        json.dumps(results.to_dict(), indent=2, default=str)
    )
    try:
        write_html_report(results, output_dir / "report.html")
    except Exception:
        logger.exception("Could not render the HTML report")
    logger.info("Benchmark results written to '%s'", output_dir)


def write_html_report(results: BenchmarkResults, path: Path) -> None:
    """Render the per-query statistics table."""
    import polars as pl
    from great_tables import GT, loc, md, style

    stats = results.query_stats()
    if not stats:
        path.write_text("<html><body><p>No query was executed.</p></body></html>")
        return

    columns = ["n", "failures", "min", "max", "avg", "std", "median", "p95", "cv"]
    rows = []
    for query, s in stats.items():
        timed = [x for x in results.samples[query] if not x["warmup"]]
        rows.append(
            {
                "query": str(query),
                **{c: s[c] for c in columns},
                "raw": [
                    float(x["seconds"]) if x["error"] is None else -1.0 for x in timed
                ],
            }
        )
    df = pl.DataFrame(
        rows,
        schema_overrides={
            **{c: pl.Float64 for c in columns[2:]},
            "raw": pl.List(pl.Float32),
        },
    )
    cfg = results.configuration
    status = "complete" if results.complete else "INCOMPLETE"
    table = (
        GT(df)
        .tab_header(
            title="TPC-H benchmark (seconds)",
            subtitle=md(
                f"Scale factor **{cfg.get('sf')}** - ambient mesh "
                f"**{cfg.get('ambient')}** - COS **{cfg.get('cos')}** - "
                f"{cfg.get('runs')} run(s) - {date.today()} - **{status}**"
            ),
        )
        .fmt_nanoplot(columns="raw")
        .fmt_number(columns=columns[2:8], decimals=2, drop_trailing_zeros=True)
        .fmt_number(columns="cv", decimals=3, drop_trailing_zeros=True)
        .sub_missing(missing_text="-")
        .cols_label(query="Query #", raw="Run time*")
        .tab_style(
            style=style.text(transform="capitalize"), locations=loc.column_header()
        )
        .tab_source_note(
            md(
                "*a `-1` value in the spark line denotes a failed run. "
                "Statistics cover successful timed runs only (warm-up excluded). "
                "`std` is the sample standard deviation, `cv` is `std / avg`."
            )
        )
    )
    if results.errors:
        table = table.tab_source_note(md("**Errors:** " + "; ".join(results.errors)))
    table.write_raw_html(str(path))


def kubectl(*args: str, check: bool = True) -> str:
    """Run kubectl and return stdout."""
    proc = subprocess.run(
        ["kubectl", *args], capture_output=True, text=True, check=check
    )
    return proc.stdout


def capture_engine_logs(
    namespace: str, run_label: str, logs_dir: Path, results: BenchmarkResults
) -> None:
    """Save runtime logs of the driver and executor pods of this run's engine.

    Pods are selected by the label injected into the engine's Spark configuration.
    A pod whose logs were saved earlier and has since disappeared keeps its file.
    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    try:
        pods = json.loads(
            kubectl(
                "get",
                "pods",
                "-n",
                namespace,
                "-l",
                f"{ENGINE_LABEL}={run_label}",
                "-o",
                "json",
            )
        )["items"]
    except Exception as e:
        logger.exception("Could not list the Spark engine pods")
        results.logs.setdefault("errors", []).append(f"list pods: {e}")
        return

    for pod in pods:
        name = pod["metadata"]["name"]
        entry = results.logs.setdefault("pods", {}).setdefault(name, {})
        entry.update(
            role=pod["metadata"].get("labels", {}).get("spark-role"),
            phase=pod["status"].get("phase"),
            created=pod["metadata"].get("creationTimestamp"),
        )
        proc = subprocess.run(
            [
                "kubectl",
                "logs",
                "-n",
                namespace,
                name,
                "--all-containers",
                "--timestamps",
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            (logs_dir / f"{name}.log").write_text(proc.stdout)
            entry.update(file=f"logs/{name}.log", captured=True, error=None)
        else:
            entry.update(captured=entry.get("captured", False), error=proc.stderr)
            logger.warning("Could not read logs of pod %s: %s", name, proc.stderr)
