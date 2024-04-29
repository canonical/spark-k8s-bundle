import logging
import os
import time
from pathlib import Path

import pytest
import pytest_asyncio
import requests
import spark8t.domain
import yaml
from pytest_operator.plugin import OpsTest
from spark8t.domain import ServiceAccount

from spark_test.core.s3 import Bucket
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account

from .helpers import (
    Bundle,
    deploy_bundle,
    local_tmp_folder,
    render_yaml,
    set_s3_credentials,
)
from .terraform import Terraform

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"


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


def generate_tmp_file(data: dict, tmp_folder: Path) -> Path:
    import uuid

    (file := tmp_folder / f"{uuid.uuid4().hex}.yaml").write_text(yaml.dump(data))
    return file


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


async def deploy_bundle_yaml(
    bundle: Bundle,
    service_account: ServiceAccount,
    bucket: Bucket,
    cos: str | None,
    ops_test: OpsTest,
) -> list[str]:
    """Deploy the Bundle in YAML format.

    Args:
        bundle: Bundle object
        service_account: Kyuubi service account to be used
        bucket: S3 bucket to be used in the deployment
        ops_test: OpsTest class

    Returns:
        list of charms deployed
    """

    data = {
        "namespace": service_account.namespace,
        "service_account": service_account.name,
        "bucket": bucket.bucket_name,
        "s3_endpoint": bucket.s3.meta.endpoint_url,
    } | ({"cos_controller": ops_test.controller_name, "cos_model": cos} if cos else {})

    bundle_content = bundle.map(lambda path: render_yaml(path, data, ops_test))

    with local_tmp_folder("tmp") as tmp_folder:
        logger.info(tmp_folder)

        bundle_tmp = bundle_content.map(
            lambda bundle_data: generate_tmp_file(bundle_data, tmp_folder)
        )

        retcode, stdout, stderr = await deploy_bundle(ops_test, bundle_tmp)

        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        logger.info(stdout)

    charms: Bundle[list[str]] = bundle_content.map(
        lambda bundle_data: list(bundle_data["applications"].keys())
    )

    return charms.main + sum(charms.overlays, [])


async def deploy_bundle_terraform(
    bundle: Terraform,
    service_account: ServiceAccount,
    bucket: Bucket,
    cos: str | None,
    ops_test: OpsTest,
) -> list[str]:
    tf_vars = {
        "s3": {
            "bucket": bucket.bucket_name,
            "endpoint": bucket.s3.meta.endpoint_url,
        },
        "kyuubi_user": service_account.name,
        "model": ops_test.model_name,
    } | ({"cos_model": cos} if cos else {})

    outputs = bundle.apply(tf_vars=tf_vars)

    return list(outputs["charms"]["value"].values())


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

    print(applications)

    await ops_test.model.wait_for_idle(
        apps=applications,
        timeout=2500,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    for app in applications:
        assert ops_test.model.applications[app].status == "active"
