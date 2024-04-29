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


@pytest_asyncio.fixture(scope="module")
async def cos(ops_test: OpsTest, cos_model):
    if cos_model and cos_model not in ops_test.models:

        base_url = (
            "https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays"
        )

        overlays = ["offers-overlay.yaml", "testing-overlay.yaml"]

        def create_file(path: Path, response: requests.Response):
            path.write_text(response.content.decode("utf-8"))
            return path

        with local_tmp_folder("tmp-cos") as tmp_folder:
            logger.info(tmp_folder)

            cos_bundle = Bundle[str | Path](
                main="cos-lite",
                overlays=[
                    create_file(tmp_folder / overlay, response)
                    for overlay in overlays
                    if (response := requests.get(f"{base_url}/{overlay}"))
                    if response.status_code == 200
                ],
            )

            await ops_test.track_model(COS_ALIAS, model_name=cos_model)

            with ops_test.model_context(COS_ALIAS) as model:

                retcode, stdout, stderr = await deploy_bundle(ops_test, cos_bundle)
                assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
                logger.info(stdout)

                await model.create_offer("traefik:ingress")

            time.sleep(15)

        yield cos_model

        await ops_test.forget_model(cos_model)
    else:
        if cos_model:
            await ops_test.track_model(COS_ALIAS, model_name=cos_model)

        yield cos_model

        if cos_model:
            await ops_test.forget_model(cos_model)


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(
    ops_test: OpsTest, credentials, bucket, registry, service_account, bundle, cos
):
    """Deploy the bundle."""

    data = {
        "namespace": service_account.namespace,
        "service_account": service_account.name,
        "bucket": bucket.bucket_name,
        "s3_endpoint": bucket.s3.meta.endpoint_url,
    } | ({"cos_controller": ops_test.controller_name, "cos_model": cos} if cos else {})

    with local_tmp_folder("tmp") as tmp_folder:
        logger.info(tmp_folder)

        bundle_rendered = bundle.map(
            lambda path: render_yaml(path, data, ops_test)
        ).map(lambda data: generate_tmp_file(data, tmp_folder))

        retcode, stdout, stderr = await deploy_bundle(ops_test, bundle_rendered)

        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        logger.info(stdout)

    await ops_test.model.wait_for_idle(
        apps=["s3"], timeout=600, idle_period=30, status="blocked"
    )

    await set_s3_credentials(ops_test, credentials)

    applications = list(render_yaml(bundle.main, data, ops_test)["applications"].keys())

    print(applications)

    await ops_test.model.wait_for_idle(
        apps=applications, timeout=1800, idle_period=30, status="active"
    )

    for app in applications:
        assert ops_test.model.applications[app].status == "active"


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_run_job(
    ops_test: OpsTest, registry, service_account, pod, credentials, bucket
):
    """Run a spark job."""

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
            "--class",
            "org.apache.spark.examples.SparkPi",
            "local:///opt/spark/examples/jars/spark-examples_2.12-3.4.2.jar",
            "1000",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

    line_check = filter(lambda line: "Pi is roughly" in line, driver_pods[0].logs())
    assert next(line_check)
    integration_hub_conf = get_secret_data(
        service_account.namespace, service_account.name
    )
    logger.info(f"Integration Hub confs: {integration_hub_conf}")

    # check that logs are in s3 folder

    confs = registry.get(service_account.id).configurations
    logger.info(f"Configurations: {confs.props}")
    s3_folder = confs.props["spark.eventLog.dir"]
    logger.info(f"Log folder: {s3_folder}")

    objects = list_s3_objects("spark-events", bucket.bucket_name, credentials)
    logger.info(f"Objects: {objects}")
    driver_pod_name = driver_pods[0].pod_name
    logger.info(f"Pod name: {driver_pod_name}")

    logger.info(f"metadata: {driver_pods[0].metadata()}")

    spark_app_selector = driver_pods[0].labels()["spark-app-selector"]

    logs_discovered = False
    for obj in objects:
        if spark_app_selector in obj:
            logs_discovered = True

    assert logs_discovered

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
            sleep(20)  # type: ignore

    assert len(apps) == 1

    # check that logs are sent to prometheus pushgateway
