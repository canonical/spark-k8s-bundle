#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import psycopg2
import pytest
from pytest_operator.plugin import OpsTest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account

from .helpers import (
    Bundle,
    deploy_bundle_terraform,
    deploy_bundle_yaml,
    get_kyuubi_credentials,
    get_postgresql_credentials,
    set_s3_credentials,
)

logger = logging.getLogger(__name__)

METASTORE_DATABASE_NAME = "hivemetastore"


@pytest.fixture(scope="module")
def bucket_name():
    return "spark-bucket"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(
    ops_test: OpsTest, credentials, bucket, service_account, bundle, cos
):
    """Deploy the bundle."""

    applications = await (
        deploy_bundle_yaml(bundle, service_account, bucket, cos, ops_test)
        if isinstance(bundle, Bundle)
        else deploy_bundle_terraform(bundle, service_account, bucket, cos, ops_test)
    )

    if "s3" in applications:
        await ops_test.model.wait_for_idle(
            apps=["s3"], timeout=600, idle_period=30, status="blocked"
        )

        await set_s3_credentials(ops_test, credentials)

    logger.info(f"Applications: {applications}")

    await ops_test.model.wait_for_idle(
        apps=applications,
        timeout=2500,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    for app in applications:
        assert ops_test.model.applications[app].status == "active"


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_invalid_authentication(ops_test, service_account):
    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")
    credentials["password"] = "something-random"

    from spark_test.core.kyuubi import KyuubiClient

    with pytest.raises(Exception) as e:
        client = KyuubiClient(**credentials)
        client.get_database("spark_test")

        assert "Error validating the login" in str(e)


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_jdbc_endpoint(ops_test: OpsTest, service_account):
    """Use JDBC Kyuubi Endpoint."""

    credentials = await get_kyuubi_credentials(ops_test, "kyuubi")

    from spark_test.core.kyuubi import KyuubiClient

    client = KyuubiClient(**credentials)

    db_name, table_name = "spark_test", "my_table"

    # Create a database
    db = client.get_database(db_name)

    assert db_name in client.databases

    table = db.create_table(
        table_name, [("name", str), ("country", str), ("year_birth", int)]
    )

    assert table_name in db.tables

    table.insert(
        ("messi", "argentina", 1987), ("sinner", "italy", 2002), ("jordan", "usa", 1963)
    )

    assert len(list(table.rows())) == 3


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_postgresql_metastore_is_used(ops_test: OpsTest):
    "Test that PostgreSQL metastore is being used by Kyuubi in the bundle."
    metastore_credentials = await get_postgresql_credentials(ops_test, "metastore")
    connection = psycopg2.connect(
        host=metastore_credentials["host"],
        database=METASTORE_DATABASE_NAME,
        user=metastore_credentials["username"],
        password=metastore_credentials["password"],
    )

    db_name, table_name = "spark_test", "my_table"

    # Fetch number of new db and tables that have been added to metastore
    num_dbs = num_tables = 0
    with connection.cursor() as cursor:
        cursor.execute(f""" SELECT * FROM "DBS" WHERE "NAME" = '{db_name}' """)
        num_dbs = cursor.rowcount
        cursor.execute(f""" SELECT * FROM "TBLS" WHERE "TBL_NAME" = '{table_name}' """)
        num_tables = cursor.rowcount

    connection.close()

    # Assert that new database and tables have indeed been added to metastore
    assert num_dbs != 0
    assert num_tables != 0
