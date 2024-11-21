import json
import logging
import time
import urllib.request

import pytest
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile
from tenacity import Retrying, stop_after_attempt, wait_fixed

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import (
    registry,
    service_account,
    small_profile_properties,
)
from spark_test.utils import get_spark_drivers

from .helpers import (
    all_prometheus_exporters_data,
    assert_logs,
    get_cos_address,
    get_secret_data,
    juju_sleep,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"
HISTORY_SERVER = "history-server"
PUSHGATEWAY = "pushgateway"
PROMETHEUS = "prometheus"
LOKI = "loki"


@pytest.fixture(scope="module")
def bucket_name():
    return "spark-bucket"


@pytest.fixture
def pod_name():
    return "my-testpod"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(ops_test, spark_bundle):
    """Test whether the bundle has deployed successfully."""
    async for applications in spark_bundle:
        for app_name in applications:
            assert ops_test.model.applications[app_name].status == "active"


@pytest.fixture
def spark_properties(small_profile_properties, image_properties):
    return small_profile_properties + image_properties


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_run_job(
    ops_test: OpsTest,
    registry,
    service_account,
    pod,
    credentials,
    bucket,
    spark_properties,
):
    """Run a spark job."""

    # upload data
    bucket.upload_file("tests/integration/resources/example.txt")

    # upload script
    bucket.upload_file("tests/integration/resources/spark_test.py")

    registry.set_configurations(service_account.id, spark_properties)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "-v",
            f"s3a://{bucket.bucket_name}/spark_test.py",
            f"-f s3a://{bucket.bucket_name}/example.txt",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

    logger.info(f"Driver pod: {driver_pods[0].pod_name}")
    logger.info("\n".join(driver_pods[0].logs()))

    line_check = filter(lambda line: "Number of lines" in line, driver_pods[0].logs())

    assert next(line_check)


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_job_logs_are_persisted(
    ops_test: OpsTest, registry, service_account, credentials, bucket
):
    integration_hub_conf = get_secret_data(
        service_account.namespace, service_account.name
    )
    logger.info(f"Integration Hub confs: {integration_hub_conf}")

    # check that logs are in s3 folder
    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1
    confs = registry.get(service_account.id).configurations
    logger.info(f"Configurations: {confs.props}")
    s3_folder = confs.props["spark.eventLog.dir"]
    logger.info(f"Log folder: {s3_folder}")
    logger.info(f"S3 objects: {bucket.list_objects()}")
    driver_pod_name = driver_pods[0].pod_name
    logger.info(f"Pod name: {driver_pod_name}")

    logger.info(f"metadata: {driver_pods[0].metadata}")

    spark_app_selector = driver_pods[0].labels["spark-app-selector"]

    logs_discovered = False
    for obj in bucket.list_objects():
        if spark_app_selector in obj["Key"]:
            logs_discovered = True

    assert logs_discovered


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_job_in_history_server(
    ops_test: OpsTest,
):
    # check that spark-history server contains the application entry
    status = await ops_test.model.get_status()

    address = status["applications"][HISTORY_SERVER]["units"][f"{HISTORY_SERVER}/0"][
        "address"
    ]

    show_unit_cmd = ["show-unit", f"{HISTORY_SERVER}/0"]

    _, stdout, _ = await ops_test.juju(*show_unit_cmd)

    logger.info(f"Show unit: {stdout}")

    for i in range(0, 5):
        try:
            logger.info(f"try n#{i} time: {time.time()}")
            apps = json.loads(
                urllib.request.urlopen(
                    f"http://{address}:18080/api/v1/applications"
                ).read()
            )
        except Exception:
            apps = []

        if len(apps) > 0:
            break
        else:
            await juju_sleep(ops_test, 30, HISTORY_SERVER)  # type: ignore
    logger.info(f"Number of apps: {len(apps)}")
    assert len(apps) == 1


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_job_in_prometheus_pushgateway(ops_test: OpsTest, cos):
    if not cos:
        pytest.skip("Not possible to test without cos")
    # check that logs are sent to prometheus pushgateway

    show_status_cmd = ["status"]

    _, stdout, _ = await ops_test.juju(*show_status_cmd)

    logger.info(f"Show status: {stdout}")

    status = await ops_test.model.get_status()
    pushgateway_address = status["applications"][PUSHGATEWAY]["units"][
        f"{PUSHGATEWAY}/0"
    ]["address"]

    for i in range(0, 5):
        try:
            logger.info(f"try n#{i} time: {time.time()}")

            metrics = json.loads(
                urllib.request.urlopen(
                    f"http://{pushgateway_address}:9091/api/v1/metrics"
                ).read()
            )
        except Exception:
            break
        if "data" in metrics and len(metrics["data"]) > 0:
            break
        else:
            await juju_sleep(ops_test, 30, HISTORY_SERVER)  # type: ignore

    assert len(metrics["data"]) > 0


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_spark_metrics_in_prometheus(
    ops_test: OpsTest, registry, service_account, cos
):
    if not cos:
        pytest.skip("Not possible to test without cos")
    show_status_cmd = ["status"]

    _, stdout, _ = await ops_test.juju(*show_status_cmd)

    logger.info(f"Show status: {stdout}")
    with ops_test.model_context(COS_ALIAS) as cos_model:
        status = await cos_model.get_status()
        prometheus_address = status["applications"][PROMETHEUS]["units"][
            f"{PROMETHEUS}/0"
        ]["address"]

        query = json.loads(
            urllib.request.urlopen(
                f"http://{prometheus_address}:9090/api/v1/query?query=push_time_seconds"
            ).read()
        )

        logger.info(f"query: {query}")
        spark_id = query["data"]["result"][0]["metric"]["exported_job"]
        logger.info(f"Spark id: {spark_id}")

        driver_pods = get_spark_drivers(
            registry.kube_interface.client, service_account.namespace
        )
        assert len(driver_pods) == 1

        logger.info(f"metadata: {driver_pods[0].metadata}")
        spark_app_selector = driver_pods[0].labels["spark-app-selector"]
        logger.info(f"Spark-app-selector: {spark_app_selector}")
        assert spark_id == spark_app_selector


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_spark_logforwaring_to_loki(
    ops_test: OpsTest, registry, service_account, cos
):
    if not cos:
        pytest.skip("Not possible to test without cos")

    _, stdout, _ = await ops_test.juju("status")

    logger.info(f"Show status: {stdout}")
    with ops_test.model_context(COS_ALIAS) as cos_model:
        status = await cos_model.get_status()
        loki_address = status["applications"][LOKI]["units"][f"{LOKI}/0"]["address"]
        assert_logs(loki_address)


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_history_server_metrics_in_cos(ops_test: OpsTest, cos):
    if not cos:
        pytest.skip("Not possible to test without cos")

    cos_model_name = cos
    # Prometheus data is being published by the app
    assert await all_prometheus_exporters_data(
        ops_test, check_field="jmx_scrape_duration_seconds", app_name=HISTORY_SERVER
    )

    # We should leave time for Prometheus data to be published
    for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
        with attempt:

            cos_address = await get_cos_address(ops_test, cos_model_name=cos_model_name)
            assert published_prometheus_data(
                ops_test, cos_model_name, cos_address, "jmx_scrape_duration_seconds"
            )

            # Alerts got published to Prometheus
            alerts_data = published_prometheus_alerts(
                ops_test, cos_model_name, cos_address
            )
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
            dashboards_info = await published_grafana_dashboards(
                ops_test, cos_model_name
            )
            logger.info(f"Dashboard info {dashboards_info}")
            assert any(
                board["title"] == "Spark History Server JMX Dashboard"
                for board in dashboards_info
            )

            # Loki logs are ingested
            logs = await published_loki_logs(
                ops_test,
                cos_model_name,
                cos_address,
                "juju_application",
                HISTORY_SERVER,
            )
            logger.info(f"Retrieved logs: {logs}")

            # check for non empty logs
            assert len(logs) > 0
            # check if startup messages are there
            c = 0
            for timestamp, message in logs.items():
                if "INFO HistoryServer" in message:
                    c = c + 1
            logger.info(f"Number of line found: {c}")
            assert c > 0
