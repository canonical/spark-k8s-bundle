import json
import logging
import socket
import subprocess
import time
from typing import cast

import boto3
import botocore
import jubilant
import psycopg2
import pytest
from tenacity import (
    Retrying,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from spark_test.core import ObjectStorageUnit
from spark_test.core.kyuubi import KyuubiClient

from .helpers import (
    get_active_kyuubi_servers_list,
    get_cos_address,
    get_kyuubi_ca_cert,
    get_kyuubi_credentials,
    get_postgresql_credentials,
    local_tmp_folder,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)
from .types import PortForwarder

logger = logging.getLogger(__name__)


METASTORE_BACKUP_BUCKET = "metastore-backup"
TEST_DB_NAME = "sparkdb"
TEST_TABLE_NAME = "sparktable"
METASTORE_DATABASE_NAME = "hivemetastore"
METASTORE_APP_NAME = "metastore"
KYUUBI_APP_NAME = "kyuubi"
BACKUP_S3_INTEGRATOR_APP_NAME = "metastore-backup"


@pytest.fixture(scope="module")
def context():
    """A common data store read+writeable by all tests."""
    context = {}
    return context


@pytest.fixture(scope="module")
def host_ip():
    """The IP address of the host running these tests."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("1.1.1.1", 80))
        return s.getsockname()[0]


@pytest.fixture(scope="module")
def certs_path():
    """A temporary directory to store certificates and keys."""
    with local_tmp_folder("temp-certs") as tmp_folder:
        yield tmp_folder


@pytest.fixture(scope="module")
def microceph_credentials(host_ip: str, certs_path):
    """Install, bootstrap and configure Microceph and return credentials."""
    logger.info("Setting up TLS certificates")
    subprocess.run(
        ["openssl", "genrsa", "-out", str(certs_path / "ca.key"), "2048"], check=True
    )
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-new",
            "-nodes",
            "-key",
            str(certs_path / "ca.key"),
            "-days",
            "1024",
            "-out",
            str(certs_path / "ca.crt"),
            "-outform",
            "PEM",
            "-subj",
            f"/C=US/ST=Denial/L=Springfield/O=Dis/CN={host_ip}",
        ],
        check=True,
    )
    subprocess.run(
        ["openssl", "genrsa", "-out", str(certs_path / "server.key"), "2048"],
        check=True,
    )
    subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-key",
            str(certs_path / "server.key"),
            "-out",
            str(certs_path / "server.csr"),
            "-subj",
            f"/C=US/ST=Denial/L=Springfield/O=Dis/CN={host_ip}",
        ],
        check=True,
    )

    with open(certs_path / "extfile.cnf", "w") as extfile:
        extfile.write(f"subjectAltName = DNS:{host_ip}, IP:{host_ip}")

    subprocess.run(
        [
            "openssl",
            "x509",
            "-req",
            "-in",
            str(certs_path / "server.csr"),
            "-CA",
            str(certs_path / "ca.crt"),
            "-CAkey",
            str(certs_path / "ca.key"),
            "-CAcreateserial",
            "-out",
            str(certs_path / "server.crt"),
            "-days",
            "365",
            "-extfile",
            str(certs_path / "extfile.cnf"),
        ],
    )

    logger.info("Setting up microceph")
    subprocess.run(
        ["sudo", "snap", "install", "microceph", "--revision", "1169"],
        check=True,
    )
    subprocess.run(
        ["sudo", "microceph", "cluster", "bootstrap"],
        check=True,
    )
    subprocess.run(
        ["sudo", "microceph", "disk", "add", "loop,1G,3"],
        check=True,
    )
    server_crt_base64 = subprocess.run(
        ["sudo", "base64", "-w0", str(certs_path / "server.crt")],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    server_key_base64 = subprocess.run(
        ["sudo", "base64", "-w0", str(certs_path / "server.key")],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    subprocess.run(
        [
            "sudo",
            "microceph",
            "enable",
            "rgw",
            "--ssl-certificate",
            server_crt_base64,
            "--ssl-private-key",
            server_key_base64,
        ],
        check=True,
    )

    output = subprocess.run(
        [
            "sudo",
            "microceph.radosgw-admin",
            "user",
            "create",
            "--uid",
            "test",
            "--display-name",
            "test",
        ],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout
    key = json.loads(output)["keys"][0]
    key_id = key["access_key"]
    secret_key = key["secret_key"]
    logger.info("Creating microceph bucket")
    for attempt in range(3):
        try:
            boto3.client(
                "s3",
                endpoint_url=f"https://{host_ip}",
                aws_access_key_id=key_id,
                aws_secret_access_key=secret_key,
                verify=certs_path / "ca.crt",
            ).create_bucket(Bucket=METASTORE_BACKUP_BUCKET)
        except botocore.exceptions.EndpointConnectionError:
            if attempt == 2:
                raise
            # microceph is not ready yet
            logger.info("Unable to connect to microceph via S3. Retrying")
            time.sleep(1)
        else:
            break
    logger.info("Microceph was setup successfully...")

    ca_crt_base64 = subprocess.run(
        ["sudo", "base64", "-w0", str(certs_path / "ca.crt")],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

    yield {
        "endpoint": f"https://{host_ip}",
        "access-key": key_id,
        "secret-key": secret_key,
        "tls-ca": ca_crt_base64,
    }

    subprocess.run(["sudo", "snap", "remove", "microceph", "--purge"], check=True)


class TestFirstDeployment:
    def test_active_status(self, juju: jubilant.Juju, spark_bundle) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(
            lambda status: jubilant.all_active(status)
            and jubilant.all_agents_idle(status),
            delay=5,
        )

    def test_ha_enabled(self, juju: jubilant.Juju) -> None:
        """Test the bundle has HA enabled, and there are exactly 3 units of Kyuubi active."""
        active_servers = get_active_kyuubi_servers_list(juju)
        assert len(active_servers) == 3

    def test_database_operations(self, juju: jubilant.Juju, context) -> None:
        """Test some read / write operations on the database."""
        credentials = get_kyuubi_credentials(juju)
        ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")
        kyuubi_client = KyuubiClient(**credentials, use_ssl=True, ca_cert=ca_cert)

        db = kyuubi_client.get_database(TEST_DB_NAME)
        assert TEST_DB_NAME in kyuubi_client.databases

        table = db.create_table(
            TEST_TABLE_NAME, [("name", str), ("country", str), ("year_birth", int)]
        )
        assert TEST_TABLE_NAME in db.tables

        table.insert(
            ("messi", "argentina", 1987),
            ("sinner", "italy", 2002),
            ("jordan", "usa", 1963),
        )
        assert len(list(table.rows())) == 3

        # Store the old admin password into context, we need this later to restore
        # this same password in the new deployment.
        context["old_admin_password"] = credentials["password"]

    def test_external_metastore_is_used(
        self, juju: jubilant.Juju, port_forward: PortForwarder
    ) -> None:
        "Test that PostgreSQL metastore is being used by Kyuubi in the bundle."
        metastore_credentials = get_postgresql_credentials(juju, METASTORE_APP_NAME)

        with port_forward(
            pod=f"{METASTORE_APP_NAME}-0", port=5432, namespace=cast(str, juju.model)
        ):
            connection = psycopg2.connect(
                host="127.0.0.1",
                database=METASTORE_DATABASE_NAME,
                user=metastore_credentials["username"],
                password=metastore_credentials["password"],
            )

            # Fetch number of new db and tables that have been added to metastore
            num_dbs = num_tables = 0
            with connection.cursor() as cursor:
                cursor.execute(
                    f""" SELECT * FROM "DBS" WHERE "NAME" = '{TEST_DB_NAME}' """
                )
                num_dbs = cursor.rowcount
                cursor.execute(
                    f""" SELECT * FROM "TBLS" WHERE "TBL_NAME" = '{TEST_TABLE_NAME}' """
                )
                num_tables = cursor.rowcount

            connection.close()

        # Assert that new database and tables have indeed been added to metastore
        assert num_dbs == 1
        assert num_tables == 1

    def test_files_in_object_storage(self, object_storage) -> None:
        """Test that the data files have indeed been created in object storage."""
        bucket: ObjectStorageUnit = object_storage
        assert bucket.exists()

        data_files = [
            blob
            for blob in bucket.list_content()
            if blob.startswith(f"warehouse/{TEST_DB_NAME}.db/{TEST_TABLE_NAME}/")
        ]
        assert len(data_files) > 0

    def test_deploy_backup_s3_integrator(
        self, juju: jubilant.Juju, microceph_credentials
    ) -> None:
        """Deploy an extra instance of s3-integrator, this time for creating Postgresql (metastore) backup."""
        juju.deploy("s3-integrator", app=BACKUP_S3_INTEGRATOR_APP_NAME, channel="edge")
        juju.wait(
            lambda status: jubilant.all_blocked(status, BACKUP_S3_INTEGRATOR_APP_NAME)
        )

        s3_endpoint = microceph_credentials["endpoint"]
        s3_access_key = microceph_credentials["access-key"]
        s3_secret_key = microceph_credentials["secret-key"]
        s3_tls_ca = microceph_credentials["tls-ca"]

        juju.config(
            BACKUP_S3_INTEGRATOR_APP_NAME,
            {
                "endpoint": s3_endpoint,
                "bucket": METASTORE_BACKUP_BUCKET,
                "region": "",
                "s3-uri-style": "path",
                "tls-ca-chain": s3_tls_ca,
            },
        )
        juju.run(
            f"{BACKUP_S3_INTEGRATOR_APP_NAME}/0",
            "sync-s3-credentials",
            {"access-key": s3_access_key, "secret-key": s3_secret_key},
        )

        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            )
        )

    def test_create_metastore_backup(self, juju: jubilant.Juju, context) -> None:
        """Create Postgres (metastore) backup."""
        juju.integrate(METASTORE_APP_NAME, BACKUP_S3_INTEGRATOR_APP_NAME)
        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            ),
            delay=10,
        )

        task = juju.run(f"{METASTORE_APP_NAME}/0", "create-backup")
        assert task.return_code == 0
        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            ),
        )

        task = juju.run(f"{METASTORE_APP_NAME}/0", "list-backups")
        assert task.return_code == 0
        results = task.results
        backup_lines = str(results["backups"]).splitlines()[2:]
        assert len(backup_lines) == 1

        backup_id = backup_lines[0].split(maxsplit=1)[0]
        logger.info(f"Found metastore DB backup with ID {backup_id}.")

        context["backup_id"] = backup_id
        context["old_model"] = juju.model


@retry(
    wait=wait_fixed(5),
    stop=stop_after_attempt(120),
    retry=retry_if_exception_type(AssertionError),
    reraise=True,
)
def test_first_deployment_destroyed(context) -> None:
    """Ensure that the first deployment has destroyed completely."""
    try:
        model_name = context["old_model"]
        subprocess.run(["juju", "status", "--model", model_name], check=True)
    except subprocess.CalledProcessError:
        # CalledProcessError being raised means the old deployment has been destroyed
        # Wait some time and return from here, since now we are ready to test new deployment
        time.sleep(10)
        return

    raise AssertionError


class TestNewDeployment:
    def test_active_status(self, juju: jubilant.Juju, spark_bundle) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(
            lambda status: jubilant.all_active(status)
            and jubilant.all_agents_idle(status),
            delay=5,
        )

    def test_ha_enabled(self, juju: jubilant.Juju) -> None:
        """Test the bundle has HA enabled, and there are exactly 3 units of Kyuubi active."""
        active_servers = get_active_kyuubi_servers_list(juju)
        assert len(active_servers) == 3

    def test_deploy_backup_s3_integrator(
        self, juju: jubilant.Juju, microceph_credentials
    ) -> None:
        """Deploy an extra instance of s3-integrator, this time for restoring Postgresql (metastore) backup."""
        juju.deploy("s3-integrator", app=BACKUP_S3_INTEGRATOR_APP_NAME, channel="edge")
        juju.wait(
            lambda status: jubilant.all_blocked(status, BACKUP_S3_INTEGRATOR_APP_NAME)
        )

        s3_endpoint = microceph_credentials["endpoint"]
        s3_access_key = microceph_credentials["access-key"]
        s3_secret_key = microceph_credentials["secret-key"]
        s3_tls_ca = microceph_credentials["tls-ca"]

        juju.config(
            BACKUP_S3_INTEGRATOR_APP_NAME,
            {
                "endpoint": s3_endpoint,
                "bucket": METASTORE_BACKUP_BUCKET,
                "region": "",
                "s3-uri-style": "path",
                "tls-ca-chain": s3_tls_ca,
            },
        )
        juju.run(
            f"{BACKUP_S3_INTEGRATOR_APP_NAME}/0",
            "sync-s3-credentials",
            {"access-key": s3_access_key, "secret-key": s3_secret_key},
        )

        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            )
        )

    def test_remove_kyuubi_and_metastore_relation(self, juju: jubilant.Juju):
        """Remove kyuubi <> metastore relation to prepare metastore for restoration of backup."""
        # It is necessary to break kyuubi <> metastore relation
        # and recreate it later for metastore restore to work
        juju.remove_relation(METASTORE_APP_NAME, f"{KYUUBI_APP_NAME}:metastore-db")
        juju.wait(
            lambda status: jubilant.all_active(
                status,
                METASTORE_APP_NAME,
                KYUUBI_APP_NAME,
                BACKUP_S3_INTEGRATOR_APP_NAME,
            )
        )

    def test_restore_metastore_backup(self, juju: jubilant.Juju, context) -> None:
        """Restore the backup from previous deployment on Postgres (metastore)."""
        juju.integrate(METASTORE_APP_NAME, BACKUP_S3_INTEGRATOR_APP_NAME)
        juju.wait(jubilant.all_agents_idle)
        juju.wait(
            lambda status: jubilant.all_active(status, BACKUP_S3_INTEGRATOR_APP_NAME)
        )
        # The postgresql instance will be in Blocked state with a message that the backup
        # detected in the S3 is from some other cluster (which in our case, is true).
        juju.wait(
            lambda status: (
                status.apps[METASTORE_APP_NAME]
                .units[f"{METASTORE_APP_NAME}/0"]
                .workload_status.current
                == "blocked"
                and status.apps[METASTORE_APP_NAME]
                .units[f"{METASTORE_APP_NAME}/0"]
                .workload_status.message.strip()
                == "the S3 repository has backups from another cluster"
            ),
            timeout=5 * 60,
            delay=5,
        )

        task = juju.run(f"{METASTORE_APP_NAME}/0", "list-backups")
        assert task.return_code == 0
        results = task.results
        backup_lines = str(results["backups"]).splitlines()[2:]
        assert len(backup_lines) == 1

        backup_id = backup_lines[0].split(maxsplit=1)[0]
        logger.info(f"Found metastore DB backup with ID {backup_id}.")

        expected_backup_id = context["backup_id"]
        assert backup_id == expected_backup_id

        task = juju.run(f"{METASTORE_APP_NAME}/0", "restore", {"backup-id": backup_id})
        assert task.return_code == 0
        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            ),
            delay=5,
        )

    def test_remove_backup_s3_integrator(self, juju: jubilant.Juju):
        """Remove the extra instance of S3 integrator after the metastore restoration is complete."""
        juju.remove_relation(METASTORE_APP_NAME, BACKUP_S3_INTEGRATOR_APP_NAME)
        juju.wait(
            lambda status: jubilant.all_active(
                status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
            ),
        )

        juju.remove_application(
            BACKUP_S3_INTEGRATOR_APP_NAME, destroy_storage=True, force=True
        )
        juju.wait(
            lambda status: jubilant.all_active(
                status, METASTORE_APP_NAME, KYUUBI_APP_NAME
            ),
        )

    def test_reintegrate_kyuubi_with_metastore(self, juju: jubilant.Juju):
        """Add backup kyuubi <> metastore relation after the metastore restoration is complete."""
        # Now re-integrate the metastore back to kyuubi
        juju.integrate(METASTORE_APP_NAME, f"{KYUUBI_APP_NAME}:metastore-db")
        juju.wait(jubilant.all_active, delay=5)

    def test_restore_admin_password(self, juju: jubilant.Juju, context):
        """Restore the admin password from the previous deployment"""
        # TODO: Implement logic to restore admin password
        # old_admin_password = context["old_admin_password"]
        # resore_admin_password(old_admin_password)
        # new_admin_password = fetch_admin_password()
        # assert old_admin_password == new_admin_password

    def test_old_tables_are_restored_in_metastore(
        self, juju: jubilant.Juju, port_forward: PortForwarder
    ) -> None:
        "Test that PostgreSQL metastore is being used by Kyuubi in the bundle."
        metastore_credentials = get_postgresql_credentials(juju, METASTORE_APP_NAME)

        with port_forward(
            pod=f"{METASTORE_APP_NAME}-0", port=5432, namespace=cast(str, juju.model)
        ):
            connection = psycopg2.connect(
                host="127.0.0.1",
                database=METASTORE_DATABASE_NAME,
                user=metastore_credentials["username"],
                password=metastore_credentials["password"],
            )

            # Fetch number of new db and tables that have been added to metastore
            num_dbs = num_tables = 0
            with connection.cursor() as cursor:
                cursor.execute(
                    f""" SELECT * FROM "DBS" WHERE "NAME" = '{TEST_DB_NAME}' """
                )
                num_dbs = cursor.rowcount
                cursor.execute(
                    f""" SELECT * FROM "TBLS" WHERE "TBL_NAME" = '{TEST_TABLE_NAME}' """
                )
                num_tables = cursor.rowcount

            connection.close()

        # Assert that the database and table are in the metastore
        assert num_dbs == 1
        assert num_tables == 1

    def test_read_previously_written_data(self, juju: jubilant.Juju, context) -> None:
        """Test some read / write operations on the database."""

        credentials = get_kyuubi_credentials(juju)
        ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")

        # TODO: Implement this once password restore mechanism is implemented
        # credentials.update({"password": context["old_admin_password"]})

        kyuubi_client = KyuubiClient(**credentials, use_ssl=True, ca_cert=ca_cert)

        assert TEST_DB_NAME in kyuubi_client.databases
        db = kyuubi_client.get_database(TEST_DB_NAME)

        assert TEST_TABLE_NAME in db.tables
        table = db.get_table(TEST_TABLE_NAME)

        table_rows = list(table.rows())
        logger.info((f"Found rows {table_rows} in the table."))

        expected_rows = [
            {"name": "messi", "country": "argentina", "year_birth": 1987},
            {"name": "sinner", "country": "italy", "year_birth": 2002},
            {"name": "jordan", "country": "usa", "year_birth": 1963},
        ]
        assert all(row in table_rows for row in expected_rows)
        assert len(table_rows) == 3

    def test_insert_new_rows(self, juju: jubilant.Juju) -> None:
        """Test that the new rows of data are being inserted on top of what's already there."""
        credentials = get_kyuubi_credentials(juju)
        ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")

        kyuubi_client = KyuubiClient(**credentials, use_ssl=True, ca_cert=ca_cert)

        db = kyuubi_client.get_database(TEST_DB_NAME)
        table = db.get_table(TEST_TABLE_NAME)

        table.insert(
            ("jumanu", "nepal", 1995),
        )
        assert len(list(table.rows())) == 4
        assert {"name": "jumanu", "country": "nepal", "year_birth": 1995} in list(
            table.rows()
        )

    def test_kyuubi_metrics_in_cos(self, cos) -> None:
        """Test that the Kyuubi metrics are visible in COS after the restoration has completed."""
        if not cos:
            pytest.skip("Not possible to test without cos")

        # We should leave time for Prometheus data to be published
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
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
                    for _, message in logs.items()
                )
