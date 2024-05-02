import json
import logging
import os.path
import shutil
import time
import urllib.request
from asyncio import sleep
from pathlib import Path

import pytest
import pytest_asyncio
import requests
import yaml
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account
from spark_test.utils import get_spark_drivers

from .helpers import (
    Bundle,
    deploy_bundle,
    deploy_bundle_terraform,
    deploy_bundle_yaml,
    generate_tmp_file,
    get_secret_data,
    list_s3_objects,
    local_tmp_folder,
    render_yaml,
    set_s3_credentials,
)

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"
HISTORY_SERVER = "history-server"
PUSHGATEWAY = "pushgateway"
PROMETHEUS = "prometheus"


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
async def test_deploy_bundle(
    ops_test: OpsTest, credentials, bucket, registry, service_account, bundle, cos
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


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_run_job(
    ops_test: OpsTest, registry, service_account, pod, credentials, bucket
):
    """Run a spark job."""

    # upload data
    bucket.upload_file("tests/integration/resources/example.txt")

    # upload script
    bucket.upload_file("tests/integration/resources/spark_test.py")

    extra_confs = PropertyFile(
        {
            "spark.kubernetes.driver.request.cores": "100m",
            "spark.kubernetes.executor.request.cores": "100m",
            "spark.kubernetes.container.image": "ghcr.io/canonical/charmed-spark:3.4-22.04_edge",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.eventLog.enabled": "true",
        }
    )

    registry.set_configurations(service_account.id, extra_confs)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "-v",
            f"s3a://{bucket.bucket_name}/spark_test.py",
            f"-b {bucket.bucket_name}",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

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

    logger.info(f"metadata: {driver_pods[0].metadata()}")

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

        logger.info(f"metadata: {driver_pods[0].metadata()}")
        spark_app_selector = driver_pods[0].labels["spark-app-selector"]
        logger.info(f"Spark-app-selector: {spark_app_selector}")
        assert spark_id == spark_app_selector
