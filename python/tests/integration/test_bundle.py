import logging
import os.path
import time
from pathlib import Path

import pytest
import requests
import yaml
from pytest_operator.plugin import OpsTest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account
from spark_test.utils import get_spark_drivers

from .helpers import set_s3_credentials

logger = logging.getLogger(__name__)


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
async def test_deploy_cos(ops_test: OpsTest):
    base_url = (
        "https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays"
    )

    overlays = ["offers-overlay.yaml", "testing-overlay.yaml"]

    await ops_test.track_model("cos", model_name="cos")

    with ops_test.model_context("cos") as cos_model:

        # Create overlays
        for overlay in overlays:
            response = requests.get(f"{base_url}/{overlay}")
            Path(overlay).write_text(response.content.decode("utf-8"))

        cmds = [
            "juju",
            "deploy",
            "--trust",
            "-m",
            f"{ops_test.model_full_name}",
            "cos-lite",
        ] + sum([["--overlay", f"./{(overlay)}"] for overlay in overlays], [])

        logger.info(" ".join(cmds))

        retcode, stdout, stderr = await ops_test.run(*cmds)
        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        logger.info(stdout)

        await cos_model.create_offer("traefik:ingress")
        time.sleep(15)

        # Delete overlays
        for overlay in overlays:
            Path(overlay).unlink()


@pytest.mark.abort_on_fail
async def test_deploy_bundle(
    ops_test: OpsTest, credentials, bucket, registry, service_account, bundle
):
    """Deploy the bundle."""
    if os.path.splitext(bundle)[1] == ".j2":
        bundle_file = ops_test.render_bundle(
            bundle,
            namespace=service_account.namespace,
            service_account=service_account.name,
            bucket=bucket.bucket_name,
            s3_endpoint=bucket.s3.meta.endpoint_url,
            cos_controller=ops_test.controller_name,
            cos_model="cos"
        )
    else:
        bundle_file = bundle

    bundle_data = yaml.safe_load(bundle_file.read_text())

    applications = []

    for app in bundle_data["applications"]:
        applications.append(app)

    (tmp_bundle := Path("bundle.yaml")).write_text(yaml.dump(bundle_data))

    cmds = [
        "deploy",
        "--trust",
        "-m",
        ops_test.model_full_name,
        f"./{tmp_bundle.name}",
    ]

    logger.info(" ".join(cmds))

    retcode, stdout, stderr = await ops_test.juju(*cmds)
    assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
    logger.info(stdout)

    tmp_bundle.unlink()

    await ops_test.model.wait_for_idle(
        apps=["s3"], timeout=2000, idle_period=30, status="blocked"
    )

    await set_s3_credentials(ops_test, credentials)

    with ops_test.model_context("cos") as cos_model:
        await cos_model.wait_for_idle(
            apps=[
                "loki",
                "grafana",
                "prometheus",
                "catalogue",
                "traefik",
                "alertmanager",
            ],
            idle_period=60,
            timeout=3600,
            raise_on_error=False,
        )

    await ops_test.model.wait_for_idle(
        apps=applications, timeout=3600, idle_period=30, status="active"
    )

    for app in applications:
        assert ops_test.model.applications[app].status == "active"
