#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import asyncio
import logging
import time
from subprocess import PIPE, check_output

import pytest
from pyhive.hive import Cursor
from pytest_operator.plugin import OpsTest

from spark_test.core.kyuubi import KyuubiClient

from .helpers import get_kyuubi_credentials, get_leader_unit_number

KYUUBI = "kyuubi"
HUB = "integration-hub"

logger = logging.getLogger(__name__)


@pytest.mark.skip_if_deployed
@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest, spark_bundle):
    await spark_bundle
    await asyncio.sleep(0)  # do nothing, await deploy_cluster


@pytest.mark.abort_on_fail
async def test_active_status(ops_test):
    """Test whether the bundle has deployed successfully."""
    for app_name in ops_test.model.applications:
        assert ops_test.model.applications[app_name].status == "active"


@pytest.mark.abort_on_fail
async def test_setup_env(ops_test: OpsTest):
    """Setup benchmark environment.

    Persist benchmark data from the connector that generates them on the fly.

    TODO: Parametrize size factor
    """
    assert ops_test.model is not None

    logger.info("Setup TPC-H connector")
    check_output(
        f"JUJU_MODEL={ops_test.model_full_name} juju remove-relation {KYUUBI} {HUB}",
        stderr=PIPE,
        shell=True,
        universal_newlines=True,
    )
    await ops_test.model.wait_for_idle(apps=[KYUUBI, HUB], idle_period=20, timeout=600)

    leader_unit_id = await get_leader_unit_number(ops_test, HUB)
    logger.info(f"Leader unit: {HUB}/{leader_unit_id}")
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "add-config",
        conf="spark.sql.catalog.tpch=org.apache.kyuubi.spark.connector.tpch.TPCHCatalog",
    )
    await action.wait()
    action = await ops_test.model.units.get(f"{HUB}/{leader_unit_id}").run_action(
        "add-config",
        conf="spark.kubernetes.container.image=docker.io/batalex/charmed-spark-kyuubi:1",
    )
    await action.wait()

    await ops_test.model.add_relation(KYUUBI, HUB)
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
                FROM tpch.sf1.{table};""")


@pytest.mark.abort_on_fail
async def test_run_benchmark_queries(ops_test: OpsTest):
    logger.info("Running benchmark queries")
    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")
    client = KyuubiClient(**credentials)

    cursor: Cursor
    with client.connection as conn, conn.cursor() as cursor:
        cursor.execute("USE bench;")
        for i in range(1, 23):
            with open(f"tests/integration/resources/sql/{i}.sql", "r") as f:
                stmt = f.read()
            start = time.monotonic()
            cursor.execute(stmt)
            cursor.fetchall()
            end = time.monotonic()
            logger.info(f"TPC-H #{i}: {end - start}")
