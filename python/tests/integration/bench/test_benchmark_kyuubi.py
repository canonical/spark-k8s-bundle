#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import logging
import time
from collections import defaultdict
from datetime import date
from subprocess import check_output
from typing import cast

import jubilant
import polars as pl
import pytest
from great_tables import GT, loc, md, style
from impala.hiveserver2 import Cursor

from spark_test.core.kyuubi import KyuubiClient

from ..helpers import get_kyuubi_credentials

KYUUBI = "kyuubi"
HUB = "integration-hub"

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def sf(request) -> str:
    """Get benchmark size factor."""
    return request.config.getoption("--bench-sf")


@pytest.fixture(scope="module")
def bench_iterations(request) -> int:
    """Get benchmark number of iterations."""
    return request.config.getoption("--bench-iterations")


@pytest.fixture(scope="module")
def report_name(request) -> str:
    """Get benchmark number of iterations."""
    return request.config.getoption("--report-name")


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


def test_setup_env(juju: jubilant.Juju, sf: str) -> None:
    """Persist benchmark data from the TPC-H generator in an isolated engine."""
    # Registry overrides are used by spark-client, not Kyuubi's managed engines.
    # Supply startup properties when opening the session, and avoid reusing an
    # existing engine that was launched without the connector JAR.
    configuration = {
        "spark.sql.catalog.tpch": "org.apache.kyuubi.spark.connector.tpch.TPCHCatalog",
        "spark.jars.packages": "org.apache.kyuubi:kyuubi-spark-connector-tpch_2.12:1.10.1",
        "kyuubi.engine.share.level": "CONNECTION",
    }
    logger.info("Persist TPC-H data from generator")
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)

    cursor: Cursor
    with client.connection as conn, conn.cursor(configuration=configuration) as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS bench;")
        for table in [
            "customer",
            "orders",
            "lineitem",
            "part",
            "partsupp",
            "supplier",
            "nation",
            "region",
        ]:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS bench.{table} AS
                SELECT *
                FROM tpch.{sf}.{table};""")


def test_run_benchmark_queries(
    juju: jubilant.Juju, sf: str, bench_iterations: int, report_name: str
) -> None:
    """Run benchmark queries and generate report."""
    logger.info("Running benchmark queries")
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)

    cursor: Cursor
    report_data = defaultdict(list)
    # The charm's testing profile uses 1 GiB executors, which are OOM-killed
    # during the sf1 joins. Isolate benchmark resources from other SQL sessions.
    configuration = {
        "kyuubi.engine.share.level": "CONNECTION",
        "spark.executor.memory": "2g",
        "spark.executor.memoryOverhead": "1g",
    }
    with client.connection as conn, conn.cursor(configuration=configuration) as cursor:
        cursor.execute("USE bench;")
        for i in range(1, 23):
            logger.info(f"Running TPC-H #{i}")
            with open(f"tests/integration/resources/sql/{i}.sql", "r") as f:
                stmt = f.read()
            for _ in range(bench_iterations):
                start = time.monotonic()
                try:
                    cursor.execute(stmt)
                    cursor.fetchall()
                except Exception:
                    logger.exception("TPC-H #%s iteration failed", i)
                    report_data[str(i)].append(None)
                else:
                    end = time.monotonic()
                    report_data[str(i)].append(end - start)

    logger.info("Creating report")
    df = pl.DataFrame(report_data)
    pivoted = df.describe().transpose(
        column_names="statistic", include_header=True, header_name="query"
    )
    table = (
        GT(
            pivoted.with_columns(
                raw=pl.Series(report_data.values(), dtype=pl.List(pl.Float32))
                .explode()
                .fill_null(-1)
                .reshape((len(report_data), -1))
                .cast(pl.List(pl.Float32))
            )
        )
        .tab_header(
            title="TPC-H benchmark (seconds)",
            subtitle=md(f"Size factor **{sf}** - {date.today()}"),
        )
        .fmt_nanoplot(columns="raw")
        .fmt_number(columns=pivoted.columns[1:], decimals=2, drop_trailing_zeros=True)
        .cols_label(query="Query #", raw="Iteration time*")
        .tab_style(
            style=style.text(transform="capitalize"), locations=loc.column_header()
        )
        .tab_source_note(md("*a `-1` value in the spark line denotes a missing value."))
    )

    table.write_raw_html(f"{report_name}.html")
    logger.info("Report written to '%s.html'", report_name)


def cleanup(juju: jubilant.Juju, service_account_registry: str) -> None:
    """Cleanup deployment.

    - Remove persisted data
    - Remove benchmark configuration from integration hub
    """
    logger.info("Cleaning bench data")
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)

    with client.connection as conn, conn.cursor() as cursor:
        cursor.execute("DROP DATABASE bench;")

    logger.info("Cleaning bench config")
    username = str(juju.config("kyuubi")["service-account"])
    check_output(
        [
            service_account_registry,
            "remove-config",
            "--username",
            username,
            "--namespace",
            cast(str, juju.model),
            "--conf",
            "spark.sql.catalog.tpch",
        ]
    )
    check_output(
        [
            service_account_registry,
            "remove-config",
            "--username",
            username,
            "--namespace",
            cast(str, juju.model),
            "--conf",
            "spark.jars.packages",
        ]
    )
