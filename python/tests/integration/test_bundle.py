import logging
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
    bundle_data = yaml.safe_load(Path(bundle).read_text())
    applications = []

    for app in bundle_data["applications"]:
        applications.append(app)

    overlay = {}
    overlay["applications"] = {
        "s3": {
            "options": {
                "bucket": bucket.bucket_name,
                "endpoint": bucket.s3.meta.endpoint_url,
            }
        },
        "kyuubi": {
            "options": {
                "service-account": service_account.name,
                "namespace": service_account.namespace,
            }
        },
    }

    Path("overlay.yaml").write_text(yaml.dump(overlay))

    cmds = [
        "juju",
        "deploy",
        "--trust",
        "-m",
        ops_test.model_full_name,
        f"./{bundle.relative_to(Path.cwd())}",
        "--overlay",
        "./overlay.yaml",
    ]

    logger.info(" ".join(cmds))

    retcode, stdout, stderr = await ops_test.run(*cmds)
    assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
    logger.info(stdout)

    await ops_test.model.wait_for_idle(
        apps=["s3"], timeout=2000, idle_period=30, status="blocked"
    )

    await set_s3_credentials(ops_test, credentials)

    Path("overlay.yaml").unlink()

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
