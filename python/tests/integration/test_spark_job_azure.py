import json
import logging
import time
import urllib.request
import uuid
from asyncio import sleep

import pytest
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile

from spark_test.fixtures.azure_storage import azure_credentials, container
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod
from spark_test.fixtures.service_account import (
    registry,
    service_account,
    small_profile_properties,
)
from spark_test.utils import get_spark_drivers

from .helpers import construct_azure_resource_uri, get_secret_data

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"
HISTORY_SERVER = "history-server"
PUSHGATEWAY = "pushgateway"
PROMETHEUS = "prometheus"


@pytest.fixture(scope="module")
def container_name():
    return f"spark-container-{uuid.uuid4()}"


@pytest.fixture
def pod_name():
    return f"my-testpod-{uuid.uuid4()}"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(ops_test, spark_bundle_with_azure_storage):
    """Test whether the bundle has deployed successfully."""
    async for applications in spark_bundle_with_azure_storage:
        for app_name in applications:
            assert ops_test.model.applications[app_name].status == "active"


@pytest.fixture
def spark_properties(small_profile_properties, image_properties):
    return small_profile_properties + image_properties


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_run_job(
    ops_test: OpsTest, registry, service_account, pod, container, spark_properties
):
    """Run a spark job."""

    # upload data
    container.upload_file("tests/integration/resources/example.txt")
    text_file_uri = construct_azure_resource_uri(container, "example.txt")

    # upload script
    container.upload_file("tests/integration/resources/spark_test.py")
    script_uri = construct_azure_resource_uri(container, "spark_test.py")

    registry.set_configurations(service_account.id, spark_properties)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "-v",
            script_uri,
            "-f",
            text_file_uri,
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
    ops_test: OpsTest, registry, service_account, container
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
    azure_storage_folder = confs.props["spark.eventLog.dir"]
    logger.info(f"Log folder: {azure_storage_folder}")
    logger.info(f"Azure storage blobs: {container.list_blobs()}")
    driver_pod_name = driver_pods[0].pod_name
    logger.info(f"Pod name: {driver_pod_name}")

    logger.info(f"metadata: {driver_pods[0].metadata}")

    spark_app_selector = driver_pods[0].labels["spark-app-selector"]

    logs_discovered = False
    for obj in container.list_blobs():
        if spark_app_selector in obj:
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
            await sleep(30)  # type: ignore
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

    metrics = json.loads(
        urllib.request.urlopen(
            f"http://{pushgateway_address}:9091/api/v1/metrics"
        ).read()
    )

    assert len(metrics["data"]) > 0


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_job_in_prometheus(ops_test: OpsTest, registry, service_account, cos):
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
