#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

import logging
from typing import cast

import jubilant
import psycopg2
import pytest
from tenacity import Retrying, stop_after_attempt, wait_fixed

from spark_test.core.kyuubi import KyuubiClient
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace  # noqa
from tests.integration.types import PortForwarder

from .helpers import (
    get_active_kyuubi_servers_list,
    get_cos_address,
    get_kyuubi_credentials,
    get_postgresql_credentials,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)

logger = logging.getLogger(__name__)

METASTORE = "metastore"
METASTORE_DATABASE_NAME = "hivemetastore"
KYUUBI_APP_NAME = "kyuubi"


@pytest.mark.skip_if_deployed
def test_deploy_bundle(spark_bundle) -> None:
    """Deploy bundle."""
    deployed_applications = spark_bundle
    logger.info(f"Deployed applications: {deployed_applications}")


def test_active_status(juju: jubilant.Juju) -> None:
    """Test whether the bundle has deployed successfully."""
    juju.wait(
        lambda status: jubilant.all_active(status) and jubilant.all_agents_idle(status),
        delay=10,
    )


def test_authentication_is_enforced(juju: jubilant.Juju) -> None:
    """Test that the authentication has been enabled in the bundle by default
    and thus Kyuubi accept connections with invalid credentials.
    """
    credentials = get_kyuubi_credentials(juju)
    credentials["password"] = "something-random"

    with pytest.raises(Exception) as e:
        client = KyuubiClient(**credentials, use_ssl=True)
        client.get_database("spark_test")

        assert "Error validating the login" in str(e)


def test_jdbc_endpoint(juju: jubilant.Juju) -> None:
    """Test that JDBC connection in Kyuubi works out of the box in bundle."""

    credentials = get_kyuubi_credentials(juju)

    logger.info("Get certificate from self-signed-certificates operator")
    status = juju.status()
    self_signed_certificate_unit = next(iter(status.apps["certificates"].units.keys()))
    task = juju.run(self_signed_certificate_unit, "get-issued-certificates")
    assert task.return_code == 0

    # items = ast.literal_eval(task.results["certificates"])
    # certificates = json.loads(items[0])
    # ca_cert = certificates["ca"]

    client = KyuubiClient(
        **credentials,
        use_ssl=True,
    )  # ca_cert=ca_cert)

    db_name, table_name = "spark_test", "my_table"

    # Create a database
    db = client.get_database(db_name)
    assert db_name in client.databases

    if table_name in db.tables:
        db.get_table(table_name).drop()

    table = db.create_table(
        table_name, [("name", str), ("country", str), ("year_birth", int)]
    )
    assert table_name in db.tables

    table.insert(
        ("messi", "argentina", 1987),
        ("sinner", "italy", 2002),
        ("jordan", "usa", 1963),
    )
    assert len(list(table.rows())) == 3


def test_postgresql_metastore_is_used(
    juju: jubilant.Juju, port_forward: PortForwarder
) -> None:
    "Test that PostgreSQL metastore is being used by Kyuubi in the bundle."
    metastore_credentials = get_postgresql_credentials(juju, METASTORE)

    with port_forward(pod=f"{METASTORE}-0", port=5432, namespace=cast(str, juju.model)):
        connection = psycopg2.connect(
            host="127.0.0.1",
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
            cursor.execute(
                f""" SELECT * FROM "TBLS" WHERE "TBL_NAME" = '{table_name}' """
            )
            num_tables = cursor.rowcount

        connection.close()

    # Assert that new database and tables have indeed been added to metastore
    assert num_dbs != 0
    assert num_tables != 0


def test_ha_deployment(juju: jubilant.Juju) -> None:
    active_servers = get_active_kyuubi_servers_list(juju)
    assert len(active_servers) == 3

    model = cast(str, juju.model)
    expected_servers = [
        f"kyuubi-0.kyuubi-endpoints.{model}.svc.cluster.local",
        f"kyuubi-1.kyuubi-endpoints.{model}.svc.cluster.local",
        f"kyuubi-2.kyuubi-endpoints.{model}.svc.cluster.local",
    ]
    assert set(active_servers) == set(expected_servers)


def test_kyuubi_metrics_in_cos(cos: str) -> None:
    if not cos:
        pytest.skip("Not possible to test without cos")

    # We should leave time for Prometheus data to be published
    for attempt in Retrying(stop=stop_after_attempt(10), wait=wait_fixed(30)):
        with attempt:
            cos_address = get_cos_address(cos_model_name=cos)
            assert published_prometheus_data(cos, cos_address, "kyuubi_jvm_uptime")

            # Alerts got published to Prometheus
            alerts_data = published_prometheus_alerts(cos, cos_address)
            assert alerts_data is not None
            logger.info(f"Alerts data: {alerts_data}")

            logger.info("Rules: ")
            for group in alerts_data["data"]["groups"]:
                for rule in group["rules"]:
                    logger.info(f"Rule: {rule['name']}")
            logger.info("End of rules.")

            for alert in [
                "KyuubiBufferPoolCapacityLow",
                "KyuubiJVMUptime",
            ]:
                assert any(
                    rule["name"] == alert
                    for group in alerts_data["data"]["groups"]
                    for rule in group["rules"]
                )

            # Grafana dashboard got published
            dashboards_info = published_grafana_dashboards(cos)
            assert dashboards_info is not None
            logger.info(f"Dashboard info {dashboards_info}")
            assert any(board["title"] == "Kyuubi" for board in dashboards_info)

            # Loki logs are ingested
            logs = published_loki_logs(
                cos,
                cos_address,
                "juju_application",
                KYUUBI_APP_NAME,
                5000,
            )
            assert logs
            logger.debug(f"Retrieved logs: {logs}")

            # check for non empty logs
            assert len(logs) > 0

            # check if Kyuubi related logs are there...
            assert any(
                "org.apache.kyuubi.session.KyuubiSessionImpl:" in message
                for timestamp, message in logs.items()
            )


def test_drop_table_if_exists(juju: jubilant.Juju) -> None:
    credentials = get_kyuubi_credentials(juju)
    client = KyuubiClient(**credentials, use_ssl=True)

    db_name, table_name = "spark_test", "my_table"

    db = client.get_database(db_name)
    db.get_table(table_name).drop()
    db.drop()
