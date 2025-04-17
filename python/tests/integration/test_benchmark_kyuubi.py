#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import asyncio
import logging
import time
from collections import defaultdict
from datetime import date

import polars as pl
import pytest
from great_tables import GT, loc, md, style
from pyhive.hive import Cursor
from pytest_operator.plugin import OpsTest

from spark_test.core.kyuubi import KyuubiClient

from .helpers import get_kyuubi_credentials, get_leader_unit_number

KYUUBI = "kyuubi"
HUB = "integration-hub"

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Add CLI options to pytest."""
    parser.addoption(
        "--foo",
        default="report",
        type=str,
        help="File name for the benchmark report.",
    )


@pytest.fixture(scope="module")
def foo(request):
    return request.config.getoption("--foo")


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


def test_something(foo):
    raise ValueError(foo)


@pytest.mark.skip_if_deployed
@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest, spark_bundle) -> None:
    """Initial deployment, ignored if we pass an existing model."""
    await spark_bundle
    await asyncio.sleep(0)  # do nothing, await deploy_cluster


@pytest.mark.abort_on_fail
async def test_active_status(ops_test: OpsTest) -> None:
    """Test whether the bundle has deployed successfully."""
    for app_name in ops_test.model.applications:
        assert ops_test.model.applications[app_name].status == "active"


@pytest.mark.abort_on_fail
async def test_setup_env(ops_test: OpsTest, sf: str) -> None:
    """Setup benchmark environment.

    - Persist benchmark data from the connector that generates them on the fly.
    - Add benchmark configuration to integration hub
    """
    assert ops_test.model is not None

    logger.info("Setup TPC-H connector")

    leader_unit_id = await get_leader_unit_number(ops_test, HUB)
    logger.info(f"Leader unit: {HUB}/{leader_unit_id}")
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "add-config",
        conf="spark.sql.catalog.tpch=org.apache.kyuubi.spark.connector.tpch.TPCHCatalog",
    )
    await action.wait()
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "add-config",
        conf="spark.jars.packages=org.apache.kyuubi:kyuubi-spark-connector-tpch_2.12:1.9.3",
    )
    await action.wait()

    async with ops_test.fast_forward(fast_interval="90s"):
        await ops_test.model.wait_for_idle(
            apps=[KYUUBI, HUB],
            status="active",
            idle_period=20,
            timeout=600,
        )

    logger.info("Persist TPC-H data from generator")
    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")
    client = KyuubiClient(**credentials)

    cursor: Cursor
    with client.connection as conn, conn.cursor() as cursor:
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
                CREATE TABLE bench.{table} AS
                SELECT *
                FROM tpch.{sf}.{table};""")


@pytest.mark.abort_on_fail
async def test_run_benchmark_queries(
    ops_test: OpsTest, sf: str, bench_iterations: int, report_name: str
) -> None:
    """Run benchmark queries and generate report."""
    logger.info("Running benchmark queries")
    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")
    client = KyuubiClient(**credentials)

    cursor: Cursor
    report_data = defaultdict(list)
    with client.connection as conn, conn.cursor() as cursor:
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
    logger.info("Report written to 'report.html'")


async def cleanup(ops_test: OpsTest) -> None:
    """Cleanup deployment.

    - Remove persisted data
    - Remove benchmark configuration from integration hub
    """
    logger.info("Cleaning bench data")
    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")
    client = KyuubiClient(**credentials)

    with client.connection as conn, conn.cursor() as cursor:
        cursor.execute("DROP DATABASE bench;")

    logger.info("Cleaning bench config")
    leader_unit_id = await get_leader_unit_number(ops_test, HUB)
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "remove-config",
        key="spark.sql.catalog.tpch",
    )
    await action.wait()
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "remove-config",
        conf="spark.jars.packages",
    )
    await action.wait()
    await ops_test.model.wait_for_idle(apps=[KYUUBI, HUB], idle_period=20, timeout=600)
