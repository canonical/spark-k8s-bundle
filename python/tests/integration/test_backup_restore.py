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
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from spark_test.core.kyuubi import KyuubiClient
from spark_test.core.s3 import Bucket

from .helpers import (
    get_kyuubi_ca_cert,
    get_kyuubi_credentials,
    get_postgresql_credentials,
    local_tmp_folder,
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
    context = {}
    return context


@pytest.fixture(scope="module")
def host_ip():
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


@pytest.mark.usefixtures("spark_bundle")
class TestFirstDeployment:
    @pytest.mark.skip_if_deployed
    def test_deploy_bundle(self, spark_bundle):
        """Deploy bundle."""
        deployed_applications = spark_bundle
        logger.info(f"Deployed applications: {deployed_applications}")

    def test_active_status(self, juju: jubilant.Juju) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(jubilant.all_active, delay=5)

    def test_database_operations(self, juju: jubilant.Juju, context) -> None:
        """Test some read / write operations on the database."""
        credentials = get_kyuubi_credentials(juju, "kyuubi")
        ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")
        print(ca_cert)
        print(credentials)
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
        bucket: Bucket = object_storage
        assert bucket.exists()

        data_files = [
            blob
            for blob in bucket.list_objects()
            if blob["Key"].startswith(f"warehouse/{TEST_DB_NAME}.db/{TEST_TABLE_NAME}/")
            and blob["Size"] > 0
        ]
        assert len(data_files) > 0

    def test_deploy_backup_s3_integrator(
        self, juju: jubilant.Juju, microceph_credentials
    ) -> None:
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
    try:
        model_name = context["old_model"]
        subprocess.run(["juju", "status", "--model", model_name], check=True)
    except subprocess.CalledProcessError:
        # CalledProcessError being raised means the old deployment has been destroyed
        # Wait some time and return from here, since now we are ready to test new deployment
        time.sleep(10)
        return

    raise AssertionError


@pytest.mark.usefixtures("spark_bundle")
class TestNewDeployment:
    def test_active_status(self, juju: jubilant.Juju) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(jubilant.all_active, delay=5)

    def test_deploy_backup_s3_integrator(
        self, juju: jubilant.Juju, microceph_credentials
    ) -> None:
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
        # It is necessary to break and recreate kyuubi <> metastore relation for metastore restore to work
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
        # Now re-integrate the metastore back to kyuubi
        juju.integrate(METASTORE_APP_NAME, f"{KYUUBI_APP_NAME}:metastore-db")
        juju.wait(jubilant.all_active, delay=5)

        # /opt/hive/bin/schematool -validate should return 0
        output = juju.ssh(
            f"{KYUUBI_APP_NAME}/0",
            command="/opt/hive/bin/schematool.sh -validate -dbType postgres",
            container="kyuubi",
        )
        assert "Done with metastore validation: [SUCCESS]" in output

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

        credentials = get_kyuubi_credentials(juju, "kyuubi")
        ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")

        # TODO: Re-enable this once password restore mechanism is implemented
        # assert context["old_admin_password"] == credentials["password"]

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
        credentials = get_kyuubi_credentials(juju, "kyuubi")
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
