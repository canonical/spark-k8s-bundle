import logging
import re
from pathlib import Path
from typing import cast

import boto3.session
import httpx
import jubilant
import pytest
from azure.storage.blob import BlobServiceClient
from botocore.client import Config
from tenacity import Retrying, stop_after_attempt, wait_fixed

from spark_test.core.azure_storage import Container
from spark_test.core.azure_storage import Credentials as AzureCreds
from spark_test.core.pod import Pod
from spark_test.core.s3 import Bucket
from spark_test.fixtures.k8s import envs, interface, kubeconfig  # noqa
from spark_test.fixtures.pod import pod  # noqa
from spark_test.fixtures.service_account import (
    registry,  # noqa
    service_account,  # noqa
    small_profile_properties,  # noqa
)
from spark_test.utils import get_spark_drivers

from .helpers import (
    JMX_EXPORTER_PORT,
    assert_logs,
    get_cos_address,
    get_secret_data,
    prometheus_exporter_data,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)
from .types import PortForwarder

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"
HISTORY_SERVER = "history-server"
PUSHGATEWAY = "pushgateway"
PROMETHEUS = "prometheus"
LOKI = "loki"


@pytest.fixture
def spark_properties(small_profile_properties, image_properties):
    return small_profile_properties + image_properties


@pytest.fixture(scope="module")
def tmp_folder(tmp_path_factory):
    return tmp_path_factory.mktemp("data")


@pytest.mark.skip_if_deployed
def test_deploy_bundle(spark_bundle):
    pass


def test_active_status(juju: jubilant.Juju) -> None:
    """Test whether the bundle has deployed successfully."""
    juju.wait(jubilant.all_active)


def test_run_job(
    juju: jubilant.Juju,
    registry,
    service_account,
    pod,
    credentials,
    object_storage,
    spark_properties,
    tmp_folder,
):
    """Run a spark job."""

    # upload data
    object_storage.upload_file("tests/integration/resources/example.txt")

    # upload script
    object_storage.upload_file("tests/integration/resources/spark_test.py")

    registry.set_configurations(service_account.id, spark_properties)

    initial_driver_pods = {
        pod.pod_name
        for pod in get_spark_drivers(
            registry.kube_interface.client, service_account.namespace
        )
    }

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "-v",
            object_storage.get_uri("spark_test.py"),
            f"-f {object_storage.get_uri('example.txt')}",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == len(initial_driver_pods) + 1

    driver_pod = [pod for pod in driver_pods if pod.pod_name not in initial_driver_pods]

    assert len(driver_pod) == 1

    logger.info(f"Driver pod: {driver_pod[0].pod_name}")
    logger.info("\n".join(driver_pod[0].logs()))

    line_check = filter(lambda line: "Number of lines" in line, driver_pod[0].logs())

    assert next(line_check)

    # write out spark_job_id to be used elsewhere
    driver_pod[0].write(tmp_folder / "spark-job-driver.json")


def test_job_logs_are_persisted(
    juju: jubilant.Juju,
    registry,
    service_account,
    credentials,
    object_storage,
    tmp_folder,
):
    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")

    # Test that logs are persisted in object storage
    integration_hub_conf = get_secret_data(
        service_account.namespace, service_account.name
    )
    logger.info(f"Integration Hub confs: {integration_hub_conf}")

    confs = registry.get(service_account.id).configurations
    logger.info(f"Configurations: {confs.props}")
    log_folder = confs.props["spark.eventLog.dir"]

    # Against a live deployment, the object storage configured might not be the one created in the tests
    # We need to retrieve everything from the integration hub
    if "spark.hadoop.fs.s3a.access.key" in confs.props:
        access_key = confs.props["spark.hadoop.fs.s3a.access.key"]
        secret_key = confs.props["spark.hadoop.fs.s3a.secret.key"]
        endpoint = confs.props["spark.hadoop.fs.s3a.endpoint"]
        log_match = re.match(r"s3a://(?P<bucket>.*)/(?P<path>.*)", log_folder)
        assert log_match is not None
        bucket_name = log_match.group("bucket")
        session = boto3.session.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        s3 = session.client(
            "s3",
            endpoint_url=credentials.endpoint,
            config=Config(
                connect_timeout=60,
                retries={"max_attempts": 0},
                request_checksum_calculation="when_supported",
                response_checksum_validation="when_supported",
            ),
        )

        object_storage = Bucket(s3, bucket_name)

    else:
        conf_key = next(key for key in confs.props if "spark.hadoop" in key)
        storage_match = re.match(
            r"spark\.hadoop\.fs\.azure\.account\.key\.(?P<account>.*)\.(?:dfs|blob).core.windows.net",
            conf_key,
        )
        assert storage_match is not None
        storage_account = storage_match.group("account")
        secret_key = confs.props[conf_key]
        credentials = AzureCreds(secret_key, storage_account)
        client = BlobServiceClient.from_connection_string(credentials.connection_string)
        endpoint, _, _ = log_folder.rpartition("/")
        container_match = re.search(r"\:\/\/(?P<container>.*)@", endpoint)
        assert container_match is not None
        container_name = container_match.group("container")

        object_storage = Container(client, container_name, credentials)

    logger.info(f"Log folder: {log_folder}")
    logger.info(f"Objects: {object_storage.list_content()}")

    logger.info(f"metadata: {driver_pod.metadata}")

    spark_app_selector = driver_pod.labels["spark-app-selector"]

    logs_discovered = False
    for obj in object_storage.list_content():
        if spark_app_selector in obj:
            logs_discovered = True

    assert logs_discovered


def test_job_in_history_server(
    juju: jubilant.Juju, tmp_folder, port_forward: PortForwarder
) -> None:
    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")
    show_unit_cmd = ["show-unit", f"{HISTORY_SERVER}/0"]
    stdout = juju.cli(*show_unit_cmd)
    logger.info(f"Show unit: {stdout}")
    spark_id = driver_pod.labels["spark-app-selector"]
    logger.info(f"Spark ID: {spark_id}")

    apps = []
    with port_forward(
        pod=f"{HISTORY_SERVER}-0", port=18080, namespace=cast(str, juju.model)
    ):
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
            with attempt:
                raw_apps = httpx.get(
                    "http://127.0.0.1:18080/api/v1/applications"
                ).json()
                logger.info(f"apps: {raw_apps}")
                apps = [app for app in raw_apps if app["id"] == spark_id]
                assert len(apps) == 1


def test_job_not_in_prometheus_pushgateway(
    juju: jubilant.Juju, cos, tmp_folder: Path, port_forward: PortForwarder
) -> None:
    """Once the job is completed, we don't expect the prometheus pushgateway to hold any data."""
    if not cos:
        pytest.skip("Not possible to test without cos")

    # check that logs are sent to prometheus pushgateway
    show_status_cmd = ["status"]
    stdout = juju.cli(*show_status_cmd)
    logger.info(f"Show status: {stdout}")
    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")
    spark_id = driver_pod.labels["spark-app-selector"]
    logger.info(f"Spark id: {spark_id}")

    metrics = {}
    with port_forward(
        pod=f"{PUSHGATEWAY}-0", port=9091, namespace=cast(str, juju.model)
    ):
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
            with attempt:
                metrics = httpx.get("http://127.0.0.1:9091/api/v1/metrics").json()
                logger.info(f"query: {metrics}")
                match metrics:
                    case {"status": "success", "data": []}:
                        pass

                    case {"status": status} if status != "success":
                        raise AssertionError

                    case {"status": "success", "data": list(metrics)}:
                        # We only check for the job we are interested in,
                        # in case this step is run against a live deployment
                        # where something else is happening
                        assert not any(
                            metric["labels"]["job"] == spark_id for metric in metrics
                        )

                    case _:
                        raise AssertionError("Unknown data format")


def test_spark_metrics_in_prometheus(
    juju: jubilant.Juju,
    registry,
    service_account,
    cos,
    tmp_folder,
    port_forward: PortForwarder,
) -> None:
    if not cos:
        pytest.skip("Not possible to test without cos")

    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")

    show_status_cmd = ["status"]

    stdout = juju.cli(*show_status_cmd)

    logger.info(f"Show status: {stdout}")
    logger.info(f"Spark id: {driver_pod.labels['spark-app-selector']}")
    # NOTE: 9090 seems to be commonly in use in some deployments.
    with port_forward(pod=f"{PROMETHEUS}-0", port=9090, namespace=cos, on_port=19090):
        for attempt in Retrying(
            stop=stop_after_attempt(5), wait=wait_fixed(30), reraise=True
        ):
            with attempt:
                query = httpx.get(
                    "http://127.0.0.1:19090/api/v1/query?query=push_time_seconds%5B20m%5D"
                ).json()  # "push_time_seconds[20m]" quoted

                logger.info(f"query: {query}")
                spark_ids = [
                    result["metric"]["exported_job"]
                    for result in query["data"]["result"]
                ]
                logger.info(f"Spark ids: {spark_ids}")

                assert driver_pod.labels["spark-app-selector"] in spark_ids


def test_spark_logforwaring_to_loki(
    juju: jubilant.Juju, registry, service_account, cos, port_forward: PortForwarder
) -> None:
    if not cos:
        pytest.skip("Not possible to test without cos")

    stdout = juju.cli("status")
    logger.info(f"Show status: {stdout}")

    with port_forward(pod=f"{LOKI}-0", port=3100, namespace=cos):
        assert_logs("127.0.0.1")


def test_history_server_metrics_in_cos(
    juju: jubilant.Juju, cos, port_forward: PortForwarder
) -> None:
    if not cos:
        pytest.skip("Not possible to test without cos")

    # Prometheus data is being published by the app
    with port_forward(
        pod=f"{HISTORY_SERVER}-0",
        port=JMX_EXPORTER_PORT,
        namespace=cast(str, juju.model),
    ):
        logger.info("Accessing prometheus")
        result = prometheus_exporter_data(host="127.0.0.1", port=JMX_EXPORTER_PORT)
        assert result is not None
        assert "jmx_scrape_duration_seconds" in result

    # We should leave time for Prometheus data to be published
    for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
        with attempt:
            cos_address = get_cos_address(cos_model_name=cos)
            assert published_prometheus_data(
                cos, cos_address, "jmx_scrape_duration_seconds"
            )

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
                "Spark History Server Missing",
                "Spark History Server Threads Dead Locked",
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
            assert any(
                board["title"] == "Spark History Server JMX Dashboard"
                for board in dashboards_info
            )

            # Loki logs are ingested
            logs = published_loki_logs(
                cos,
                cos_address,
                "juju_application",
                HISTORY_SERVER,
            )
            logger.info(f"Retrieved logs: {logs}")

            # check for non empty logs
            assert len(logs) > 0
            # check if startup messages are there
            c = 0
            for _timestamp, message in logs.items():
                if "INFO FsHistoryProvider" in message:
                    c = c + 1
            logger.info(f"Number of line found: {c}")
            assert c > 0
