#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
"""Configurable TPC-H benchmark for Charmed Apache Kyuubi.

One invocation measures one benchmark configuration (scale factor, ambient mesh
and COS settings). See the `benchmarks-kyuubi` tox environment.
"""

import logging
import shutil
import subprocess
import time
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import jubilant
import pytest
from impala.hiveserver2 import Cursor

from spark_test.core.kyuubi import KyuubiClient

from ..conftest import SPARK_VERSION
from ..helpers import get_kyuubi_credentials
from ._support import (
    ALL_QUERIES,
    ENGINE_LABEL,
    TABLES,
    BenchmarkResults,
    capture_engine_logs,
    execute_with_timeout,
    expected_row_count,
    load_query,
    row_count_is_valid,
    write_results,
)

logger = logging.getLogger(__name__)

BEACON_APP = "istio-beacon-k8s"
COS_RELATIONS = ("metrics-endpoint", "grafana-dashboard", "logging")
TPCH_CONNECTOR_CONF = {
    "spark.sql.catalog.tpch": "org.apache.kyuubi.spark.connector.tpch.TPCHCatalog",
    "spark.jars.packages": "org.apache.kyuubi:kyuubi-spark-connector-tpch_2.12:1.10.1",
    "kyuubi.engine.share.level": "CONNECTION",
}
# The charm's testing profile uses 1 GiB executors, which are OOM-killed
# during the sf1 joins.
DEFAULT_ENGINE_CONF = {
    "kyuubi.engine.share.level": "CONNECTION",
    "spark.executor.memory": "2g",
    "spark.executor.memoryOverhead": "1g",
}


@pytest.fixture(scope="module")
def database(sf: str) -> str:
    return f"bench_{sf}"


@pytest.fixture(scope="module")
def queries(request) -> list[int]:
    excluded = set(request.config.getoption("--bench-exclude-queries"))
    selected = [q for q in ALL_QUERIES if q not in excluded]
    if not selected:
        raise pytest.UsageError("All queries are excluded")
    return selected


@pytest.fixture(scope="module")
def runs(request) -> int:
    value = request.config.getoption("--bench-runs")
    if value < 1:
        raise pytest.UsageError("--bench-runs must be at least 1")
    return value


@pytest.fixture(scope="module")
def warmup(request) -> int:
    value = request.config.getoption("--bench-warmup")
    if value < 0:
        raise pytest.UsageError("--bench-warmup cannot be negative")
    return value


@pytest.fixture(scope="module", autouse=True)
def output_dir(request, report_name: str) -> Path:
    """Report directory, validated before anything is deployed."""
    path = Path(request.config.getoption("--bench-output-dir")) / report_name
    if path.exists() and any(path.iterdir()):
        if not request.config.getoption("--bench-overwrite"):
            raise pytest.UsageError(
                f"'{path}' is not empty; choose another --report-name "
                "or pass --bench-overwrite"
            )
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="module")
def results(
    request, juju, sf, runs, warmup, queries, output_dir: Path
) -> Iterator[BenchmarkResults]:
    """Results of this invocation; written to disk at module teardown."""
    config = request.config
    res = BenchmarkResults(
        configuration={
            "sf": sf,
            "ambient_requested": config.getoption("--bench-ambient"),
            "cos_requested": config.getoption("--bench-cos"),
            "runs": runs,
            "warmup": warmup,
            "queries": queries,
            "excluded_queries": config.getoption("--bench-exclude-queries"),
            "query_timeout_seconds": config.getoption("--bench-query-timeout"),
            "report_name": config.getoption("--report-name"),
            "spark_version": SPARK_VERSION,
            "storage_backend": config.getoption("--storage-backend"),
            "deployed_by_benchmark": not config.getoption("--no-deploy"),
            "model": juju.model,
        }
    )
    try:
        res.environment["git_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
    except OSError:
        pass
    yield res
    write_results(res, output_dir)


def detect_conditions(juju: jubilant.Juju) -> dict:
    """Determine the mesh and COS conditions actually present in the model."""
    status = juju.status()
    kyuubi = status.apps.get("kyuubi")
    relations = set(kyuubi.relations) if kyuubi else set()
    return {
        "ambient": BEACON_APP in status.apps,
        "cos": bool(relations.intersection(COS_RELATIONS)),
        "apps": {
            name: {
                "charm": app.charm,
                "revision": app.charm_rev,
                "channel": app.charm_channel,
                "units": len(app.units),
            }
            for name, app in status.apps.items()
        },
    }


@pytest.mark.skip_if_deployed
def test_deploy_bundle(juju: jubilant.Juju, spark_bundle) -> None:
    """Initial deployment, ignored if we pass an existing model."""
    pass


def test_active_status(juju: jubilant.Juju) -> None:
    """Test whether the bundle has deployed successfully."""
    juju.wait(
        lambda status: jubilant.all_active(status) and jubilant.all_agents_idle(status),
        delay=10,
    )


def test_verify_conditions(juju: jubilant.Juju, results: BenchmarkResults) -> None:
    """Record the actual mesh and COS conditions; abort if they differ from the request."""
    detected = detect_conditions(juju)
    results.configuration["ambient"] = detected["ambient"]
    results.configuration["cos"] = detected["cos"]
    results.environment["applications"] = detected["apps"]

    mismatches = []
    for key in ("ambient", "cos"):
        requested = results.configuration[f"{key}_requested"]
        if requested is not None and requested != detected[key]:
            mismatches.append(f"{key}: requested {requested}, found {detected[key]}")
    if mismatches:
        results.errors.append("Condition mismatch: " + "; ".join(mismatches))
        pytest.fail("Deployment does not match the requested conditions: " + "; ".join(mismatches))


def count_rows(cursor: Cursor, database: str, table: str) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {database}.{table}")
    return int(cursor.fetchall()[0][0])


def _setup_dataset(
    juju: jubilant.Juju,
    sf: str,
    database: str,
    results: BenchmarkResults,
) -> None:
    """Create the missing TPC-H tables for this scale factor and validate them."""
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)
    dataset = results.dataset
    dataset.update(database=database, created_database=False, created_tables=[])

    cursor: Cursor
    with (
        client.connection as conn,
        conn.cursor(configuration=TPCH_CONNECTOR_CONF) as cursor,
    ):
        cursor.execute("SHOW DATABASES")
        existing_dbs = {row[0] for row in cursor.fetchall()}
        if database not in existing_dbs:
            cursor.execute(f"CREATE DATABASE {database}")
            dataset["created_database"] = True

        cursor.execute(f"SHOW TABLES IN {database}")
        existing_tables = {row[1] for row in cursor.fetchall()}
        for table in TABLES:
            if table in existing_tables:
                continue
            logger.info("Persisting %s.%s from the TPC-H generator", database, table)
            cursor.execute(
                f"CREATE TABLE {database}.{table} AS SELECT * FROM tpch.{sf}.{table}"
            )
            dataset["created_tables"].append(table)

        counts = {}
        invalid = []
        for table in TABLES:
            counts[table] = count_rows(cursor, database, table)
            if not row_count_is_valid(table, sf, counts[table]):
                invalid.append(
                    f"{table}: {counts[table]} rows, expected "
                    f"~{expected_row_count(table, sf)}"
                )
        dataset["row_counts"] = counts

    if invalid:
        results.errors.append("Invalid dataset: " + "; ".join(invalid))
        pytest.fail(f"Tables in {database} do not match {sf}: " + "; ".join(invalid))


def test_setup_dataset(
    juju: jubilant.Juju, sf: str, database: str, results: BenchmarkResults
) -> None:
    """Create the missing TPC-H tables for this scale factor and validate them."""
    try:
        _setup_dataset(juju, sf, database, results)
    except Exception as e:
        if not results.errors:
            results.errors.append(f"Dataset setup failed: {e!r}"[:500])
        raise


def test_run_benchmark_queries(
    request,
    juju: jubilant.Juju,
    database: str,
    queries: list[int],
    runs: int,
    warmup: int,
    output_dir: Path,
    results: BenchmarkResults,
) -> None:
    """Run the selected queries and record timings and engine logs."""
    config = request.config
    namespace = cast(str, juju.model)
    run_label = uuid.uuid4().hex[:12]
    timeout = config.getoption("--bench-query-timeout")
    engine_conf = {
        **DEFAULT_ENGINE_CONF,
        f"spark.kubernetes.driver.label.{ENGINE_LABEL}": run_label,
        f"spark.kubernetes.executor.label.{ENGINE_LABEL}": run_label,
        **dict(config.getoption("--bench-spark-conf")),
    }
    results.configuration["engine_conf"] = engine_conf
    results.logs["selector"] = f"{ENGINE_LABEL}={run_label}"
    results.phase = "running"
    sql = {q: load_query(q) for q in queries}

    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)
    cursor: Cursor
    with client.connection as conn, conn.cursor(configuration=engine_conf) as cursor:
        try:
            cursor.execute(f"USE {database}")
            for round_ in range(-warmup + 1, runs + 1):
                is_warmup = round_ <= 0
                logger.info(
                    "Round %s (%s)", round_, "warm-up" if is_warmup else "timed"
                )
                for q in queries:
                    start = time.monotonic()
                    try:
                        execute_with_timeout(cursor, sql[q], timeout)
                    except Exception as e:
                        logger.exception("TPC-H #%s failed in round %s", q, round_)
                        results.record(q, round_, is_warmup, None, repr(e))
                    else:
                        elapsed = time.monotonic() - start
                        results.record(q, round_, is_warmup, elapsed, None)
                capture_engine_logs(
                    namespace, run_label, output_dir / "logs", results
                )
        except BaseException as e:
            results.errors.append(f"Benchmark aborted: {e!r}")
            raise
        finally:
            capture_engine_logs(namespace, run_label, output_dir / "logs", results)
    results.phase = "finished"

    failures = results.total_failures
    warmup_failures = sum(
        1 for s in results.samples.values() for x in s if x["warmup"] and x["error"]
    )
    assert failures == 0 and warmup_failures == 0, (
        f"{failures} timed and {warmup_failures} warm-up query executions failed; "
        "see results.json"
    )


def test_cleanup(
    request, juju: jubilant.Juju, database: str, results: BenchmarkResults
) -> None:
    """Drop only what this run created, when asked to."""
    if not request.config.getoption("--bench-cleanup"):
        pytest.skip("--bench-cleanup not specified")
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)
    dataset = results.dataset
    cursor: Cursor
    with client.connection as conn, conn.cursor() as cursor:
        for table in dataset.get("created_tables", []):
            cursor.execute(f"DROP TABLE IF EXISTS {database}.{table}")
        if dataset.get("created_database"):
            cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    dataset["cleaned_up"] = True
