import json
import logging
import os
import socket
import subprocess
import time
from typing import cast

import boto3
import botocore
import jubilant
import psycopg2
import pytest

from spark_test.core.kyuubi import KyuubiClient
from spark_test.core.s3 import Bucket
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .helpers import (
    get_active_kyuubi_servers_list,
    get_cos_address,
    get_kyuubi_credentials,
    get_kyuubi_ca_cert,
    get_postgresql_credentials,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)
from tests.integration.types import PortForwarder


logger = logging.getLogger(__name__)


METASTORE_BACKUP_BUCKET = "metastore-backup"
TEST_DB_NAME = "sparkdb"
TEST_TABLE_NAME = "sparktable"
METASTORE_DATABASE_NAME = "hivemetastore"
METASTORE_APP_NAME = "metastore"
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
def microceph_credentials(host_ip: str, tmp_path):
    """Install, bootstrap and configure Microceph and return credentials."""
    logger.info("Setting up TLS certificates")
    subprocess.run(["openssl", "genrsa", "-out", "./ca.key", "2048"], check=True)
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-new",
            "-nodes",
            "-key",
            "./ca.key",
            "-days",
            "1024",
            "-out",
            "./ca.crt",
            "-outform",
            "PEM",
            "-subj",
            f"/C=US/ST=Denial/L=Springfield/O=Dis/CN={host_ip}",
        ],
        check=True,
        cwd=tmp_path
    )
    subprocess.run(["openssl", "genrsa", "-out", "./server.key", "2048"], check=True, cwd=tmp_path)
    subprocess.run(
        [
            "openssl",
            "req",
            "-new",
            "-key",
            "./server.key",
            "-out",
            "./server.csr",
            "-subj",
            f"/C=US/ST=Denial/L=Springfield/O=Dis/CN={host_ip}",
        ],
        check=True,
        cwd=tmp_path
    )
    subprocess.run(
        f'echo "subjectAltName = DNS:{host_ip}, IP:{host_ip}" > ./extfile.cnf',
        shell=True,
        check=True,
        cwd=tmp_path
    )
    subprocess.run(
        [
            "openssl",
            "x509",
            "-req",
            "-in",
            "./server.csr",
            "-CA",
            "./ca.crt",
            "-CAkey",
            "./ca.key",
            "-CAcreateserial",
            "-out",
            "./server.crt",
            "-days",
            "365",
            "-extfile",
            "./extfile.cnf",
        ],
        cwd=tmp_path
    )

    logger.info("Setting up microceph")
    subprocess.run(
        ["sudo", "snap", "install", "microceph", "--revision", "1169"], check=True, cwd=tmp_path
    )
    subprocess.run(["sudo", "microceph", "cluster", "bootstrap"], check=True, cwd=tmp_path)
    subprocess.run(["sudo", "microceph", "disk", "add", "loop,1G,3"], check=True, cwd=tmp_path)
    subprocess.run(
        'sudo microceph enable rgw --ssl-certificate="$(sudo base64 -w0 ./server.crt)" --ssl-private-key="$(sudo base64 -w0 ./server.key)"',
        shell=True,
        check=True,
        cwd=tmp_path
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
        cwd=tmp_path
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
                verify="./ca.crt",
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

    ca_crt_b64 = subprocess.run(
        "sudo base64 -w0 ./ca.crt",
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        cwd=tmp_path
    ).stdout

    yield {
        "endpoint": f"https://{host_ip}",
        "access-key": key_id,
        "secret-key": secret_key,
        "tls-ca": ca_crt_b64,
    }

    subprocess.run(["sudo", "snap", "remove", "microceph", "--purge"], check=True)


@pytest.mark.usefixtures("spark_bundle")
class TestFirstDeployment:
    def test_deploy_bundle(self, spark_bundle) -> None:
        """Test that the bundle deploys fine with charms in active state."""
        pass

    def test_active_status(self, juju: jubilant.Juju) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(jubilant.all_active, delay=5)

    # def test_database_operations(self, juju: jubilant.Juju) -> None:
    #     """Test some read / write operations on the database."""
    #     credentials = get_kyuubi_credentials(juju, "kyuubi")
    #     ca_cert = get_kyuubi_ca_cert(juju, certificates_app_name="certificates")
    #     print(ca_cert)
    #     print(credentials)
    #     kyuubi_client = KyuubiClient(**credentials, use_ssl=True, ca_cert=ca_cert)

    #     db = kyuubi_client.get_database(TEST_DB_NAME)
    #     assert TEST_DB_NAME in kyuubi_client.databases

    #     table = db.create_table(
    #         TEST_TABLE_NAME, [("name", str), ("country", str), ("year_birth", int)]
    #     )
    #     assert TEST_TABLE_NAME in db.tables

    #     table.insert(
    #         ("messi", "argentina", 1987), ("sinner", "italy", 2002), ("jordan", "usa", 1963)
    #     )
    #     assert len(list(table.rows())) == 3

    # def test_external_metastore_is_used(
    #     self, juju: jubilant.Juju, port_forward: PortForwarder
    # ) -> None:
    #     "Test that PostgreSQL metastore is being used by Kyuubi in the bundle."
    #     metastore_credentials = get_postgresql_credentials(juju, METASTORE_APP_NAME)

    #     with port_forward(
    #         pod=f"{METASTORE_APP_NAME}-0", port=5432, namespace=cast(str, juju.model)
    #     ):
    #         connection = psycopg2.connect(
    #             host="127.0.0.1",
    #             database=METASTORE_DATABASE_NAME,
    #             user=metastore_credentials["username"],
    #             password=metastore_credentials["password"],
    #         )

    #         # Fetch number of new db and tables that have been added to metastore
    #         num_dbs = num_tables = 0
    #         with connection.cursor() as cursor:
    #             cursor.execute(f""" SELECT * FROM "DBS" WHERE "NAME" = '{TEST_DB_NAME}' """)
    #             num_dbs = cursor.rowcount
    #             cursor.execute(
    #                 f""" SELECT * FROM "TBLS" WHERE "TBL_NAME" = '{TEST_TABLE_NAME}' """
    #             )
    #             num_tables = cursor.rowcount

    #         connection.close()

    #     # Assert that new database and tables have indeed been added to metastore
    #     assert num_dbs == 1
    #     assert num_tables == 1

    # def test_files_in_object_storage(self, object_storage) -> None:
    #     """Test that the data files have indeed been created in object storage."""
    #     bucket: Bucket = object_storage
    #     assert bucket.exists()

    #     data_files = [
    #         blob
    #         for blob in bucket.list_objects()
    #         if blob["Key"].startswith(f"warehouse/{TEST_DB_NAME}.db/{TEST_TABLE_NAME}/") and blob["Size"] > 0
    #     ]
    #     assert len(data_files) > 0

    # def test_deploy_backup_s3_integrator(self, juju: jubilant.Juju, microceph_credentials) -> None:
    #     juju.deploy("s3-integrator", app=BACKUP_S3_INTEGRATOR_APP_NAME, channel="edge")
    #     juju.wait(
    #         lambda status: jubilant.all_blocked(status, BACKUP_S3_INTEGRATOR_APP_NAME)
    #     )

    #     s3_endpoint = microceph_credentials["endpoint"]
    #     s3_access_key = microceph_credentials["access-key"]
    #     s3_secret_key = microceph_credentials["secret-key"]
    #     s3_tls_ca = microceph_credentials["tls-ca"]

    #     juju.config(
    #         BACKUP_S3_INTEGRATOR_APP_NAME,
    #         {
    #             "endpoint": s3_endpoint,
    #             "bucket": METASTORE_BACKUP_BUCKET,
    #             "region": "",
    #             "s3-uri-style": "path",
    #             "tls-ca-chain": s3_tls_ca,
    #         },
    #     )
    #     juju.run(
    #         f"{BACKUP_S3_INTEGRATOR_APP_NAME}/0",
    #         "sync-s3-credentials",
    #         {"access-key": s3_access_key, "secret-key": s3_secret_key},
    #     )

    #     juju.wait(
    #         lambda status: jubilant.all_active(
    #             status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
    #         )
    #     )

    # def test_create_metastore_backup(self, juju: jubilant.Juju, context) -> None:
    #     juju.integrate(METASTORE_APP_NAME, BACKUP_S3_INTEGRATOR_APP_NAME)
    #     juju.wait(
    #         lambda status: jubilant.all_active(
    #             status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
    #         ),
    #         delay=10
    #     )

    #     task = juju.run(f"{METASTORE_APP_NAME}/0", "create-backup")
    #     assert task.return_code == 0
    #     juju.wait(
    #         lambda status: jubilant.all_active(
    #             status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
    #         ),
    #     )

    #     task = juju.run(f"{METASTORE_APP_NAME}/0", "list-backups")
    #     assert task.return_code == 0
    #     results = task.results
    #     backup_lines = str(results["backups"]).splitlines()[2:]
    #     assert len(backup_lines) == 1

    #     backup_id = backup_lines[0].split(maxsplit=1)[0]
    #     logger.info(f"Found metastore DB backup with ID {backup_id}.")

    #     context["backup_id"] = backup_id



@retry(
    wait=wait_fixed(5),
    stop=stop_after_attempt(120),
    retry=retry_if_exception_type(AssertionError),
    reraise=True,
)
def test_first_deployment_destroyed(juju: jubilant.Juju) -> None:
    try:
        status = juju.status()
        logger.info("Juju status: ")
        logger.info(status)
    except jubilant.CLIError:
        # CLIError being raised means the model has been destroyed
        return 
    
    raise AssertionError


@pytest.mark.usefixtures("spark_bundle")
class TestNewDeployment:
    def test_deploy_bundle(self, spark_bundle) -> None:
        """Test that the bundle deploys fine with charms in active state."""
        pass

    def test_active_status(self, juju: jubilant.Juju) -> None:
        """Test whether the bundle has deployed successfully."""
        juju.wait(jubilant.all_active, delay=5)

    # def test_deploy_backup_s3_integrator(self, juju: jubilant.Juju, microceph_credentials) -> None:
    #     juju.deploy("s3-integrator", app=BACKUP_S3_INTEGRATOR_APP_NAME, channel="edge")
    #     juju.wait(
    #         lambda status: jubilant.all_blocked(status, BACKUP_S3_INTEGRATOR_APP_NAME)
    #     )

    #     s3_endpoint = microceph_credentials["endpoint"]
    #     s3_access_key = microceph_credentials["access-key"]
    #     s3_secret_key = microceph_credentials["secret-key"]
    #     s3_tls_ca = microceph_credentials["tls-ca"]

    #     juju.config(
    #         BACKUP_S3_INTEGRATOR_APP_NAME,
    #         {
    #             "endpoint": s3_endpoint,
    #             "bucket": METASTORE_BACKUP_BUCKET,
    #             "region": "",
    #             "s3-uri-style": "path",
    #             "tls-ca-chain": s3_tls_ca,
    #         },
    #     )
    #     juju.run(
    #         f"{BACKUP_S3_INTEGRATOR_APP_NAME}/0",
    #         "sync-s3-credentials",
    #         {"access-key": s3_access_key, "secret-key": s3_secret_key},
    #     )

    #     juju.wait(
    #         lambda status: jubilant.all_active(
    #             status, BACKUP_S3_INTEGRATOR_APP_NAME, METASTORE_APP_NAME
    #         )
    #     )

    # def test_restore_metastore_backup(self, juju: jubilant.Juju, context) -> None:
    #     juju.integrate(METASTORE_APP_NAME, BACKUP_S3_INTEGRATOR_APP_NAME)
    #     juju.wait(jubilant.all_agents_idle)
    #     import time
    #     time.sleep(10)
