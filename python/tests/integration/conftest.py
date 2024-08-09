# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import shutil
import uuid
from pathlib import Path
from time import sleep

import pytest
import pytest_asyncio
import requests
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile

from spark_test.core.azure_storage import Credentials as AzureStorageCredentials
from spark_test.fixtures.azure_storage import azure_credentials, container
from spark_test.fixtures.pod import spark_image
from spark_test.fixtures.service_account import service_account
from tests import IE_TEST_DIR, RELEASE_DIR

from .helpers import (
    COS_ALIAS,
    Bundle,
    add_juju_secret,
    deploy_bundle,
    deploy_bundle_terraform,
    deploy_bundle_yaml,
    deploy_bundle_yaml_azure_storage,
    juju_sleep,
    local_tmp_folder,
    set_azure_credentials,
    set_s3_credentials,
)
from .terraform import Terraform

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Add CLI options to pytest."""
    parser.addoption(
        "--integration", action="store_true", help="flag to enable integration tests"
    )
    parser.addoption(
        "--release",
        required=False,
        help="Path to the release to be used in integration tests",
    )
    parser.addoption(
        "--bundle",
        required=False,
        help="Path to a particular bundle. Using single files for YAML bundles "
        "and directories for terraforms.",
    )
    parser.addoption(
        "--overlay",
        action="append",
        type=str,
        help="Path to the overlay to be used with the bundle.",
    )
    parser.addoption(
        "--cos-model",
        required=False,
        type=str,
        help="When provided, it deploys COS as well. "
        "If the model already exists, we assume COS had already been "
        "deployed.",
    )
    parser.addoption(
        "--backend",
        choices=["yaml", "terraform"],
        default="yaml",
        type=str,
        help="Which backend to use for bundle. Supported values are either "
        "yaml (default) or terraform.",
    )
    parser.addoption(
        "--spark-version",
        default="3.4.2",
        type=str,
        help="Which Spark version to use for bundle testing.",
    )


@pytest.fixture(scope="module")
def cos_model(request) -> None | str:
    """The name of the model in which COS is either already deployed or is to be deployed."""
    return request.config.getoption("--cos-model")


@pytest.fixture(scope="module")
def backend(request) -> None | str:
    """The backend which is to be used to deploy the bundle."""
    return request.config.getoption("--backend")


# @pytest.fixture(scope="module")
# def object_storage_backend(request) -> None | str:
#     """The object storage backend to be used in the bundle."""
#     return request.config.getoption("--object-storage-backend")


@pytest.fixture(scope="module")
def spark_version(request) -> str:
    """The backend which is to be used to deploy the bundle."""
    return request.config.getoption("--spark-version") or "3.4.2"


@pytest.fixture(scope="module")
def image_properties(spark_image):
    return PropertyFile(
        {
            "spark.kubernetes.container.image": spark_image,
        }
    )


@pytest.fixture(scope="module")
def bundle(
    request, cos, backend, spark_version, tmp_path_factory
) -> Bundle[Path] | Terraform:
    """Prepare and yield Bundle object incapsulating the apps that are to be deployed."""
    if file := request.config.getoption("--bundle"):
        bundle = Path(file)
    else:
        release_dir: Path = (
            Path(file) if (file := request.config.getoption("--release")) else None
        ) or (
            Path(
                IE_TEST_DIR
                / ".."
                / ".."
                / "releases"
                / ".".join(spark_version.split(".")[:2])
            )
        )

        bundle = (
            release_dir / "terraform"
            if backend == "terraform"
            else release_dir / "yaml" / "bundle.yaml.j2"
        )

    if backend == "terraform":
        tmp_path = tmp_path_factory.mktemp(uuid.uuid4().hex) / "terraform"
        shutil.copytree(bundle, tmp_path)
        client = Terraform(path=tmp_path)
        yield client

    else:
        overlays = (
            [Path(file) for file in files]
            if (files := request.config.getoption("--overlay"))
            else (
                [bundle.parent / "overlays" / "cos-integration.yaml.j2"] if cos else []
            )
        )

        for file in overlays + [bundle]:
            if not file.exists():
                raise FileNotFoundError(file.absolute())

        yield Bundle(main=bundle, overlays=overlays)


@pytest.fixture(scope="module")
def bundle_with_azure_storage(request, spark_version, cos) -> Bundle[Path]:
    """Prepare and yield Bundle object incapsulating the apps that are to be deployed."""
    if file := request.config.getoption("--bundle"):
        bundle = Path(file)
    else:
        release_dir: Path = (
            Path(file) if (file := request.config.getoption("--release")) else None
        ) or (
            Path(
                IE_TEST_DIR
                / ".."
                / ".."
                / "releases"
                / ".".join(spark_version.split(".")[:2])
            )
        )

        bundle = release_dir / "yaml" / "bundle-azure-storage.yaml.j2"

    overlays = (
        [Path(file) for file in files]
        if (files := request.config.getoption("--overlay"))
        else ([bundle.parent / "overlays" / "cos-integration.yaml.j2"] if cos else [])
    )

    for file in overlays + [bundle]:
        if not file.exists():
            raise FileNotFoundError(file.absolute())

    yield Bundle(main=bundle, overlays=overlays)


@pytest.fixture
def integration_test(request):
    """Specifies whether integration test is to be run or not."""
    env_flag = bool(int(os.environ.get("IE_TEST", "0")))
    cli_flag = request.config.getoption("--integration")

    if not env_flag and not cli_flag:
        pytest.skip(
            reason="Integration test, to be skipped when running unittests",
        )


@pytest_asyncio.fixture(scope="module")
async def cos(ops_test: OpsTest, cos_model):
    """
    Deploy COS bundle depending upon the value of cos_model fixture, and yield its value.
    """
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

            await juju_sleep(ops_test, 15)

        yield cos_model

        await ops_test.forget_model(cos_model)
    else:
        if cos_model:
            await ops_test.track_model(COS_ALIAS, model_name=cos_model)

        yield cos_model

        if cos_model:
            await ops_test.forget_model(cos_model)


@pytest.fixture(scope="module")
async def spark_bundle(ops_test: OpsTest, credentials, bucket, bundle, cos):
    """Deploy all applications in the Kyuubi bundle, wait for all of them to be active,
    and finally yield a list of the names of the applications that were deployed.
    """
    applications = await (
        deploy_bundle_yaml(bundle, bucket, cos, ops_test)
        if isinstance(bundle, Bundle)
        else deploy_bundle_terraform(bundle, bucket, cos, ops_test)
    )

    if "s3" in applications:
        await ops_test.model.wait_for_idle(
            apps=["s3"], timeout=600, idle_period=30, status="blocked"
        )

        await set_s3_credentials(ops_test, credentials)

    if cos:
        with ops_test.model_context(COS_ALIAS) as cos_model:
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
        apps=applications,
        timeout=3600,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    yield applications


@pytest.fixture(scope="module")
async def spark_bundle_with_azure_storage(
    ops_test: OpsTest,
    azure_credentials: AzureStorageCredentials,
    container,
    bundle_with_azure_storage,
    cos,
):
    """Deploy all applications in the Spark bundle, wait for all of them to be active,
    and finally yield a list of the names of the applications that were deployed.
    For object storage, use azure-storage-integrator.
    """
    applications = await deploy_bundle_yaml_azure_storage(
        bundle_with_azure_storage, container, cos, ops_test
    )

    if "azure-storage" in applications:
        secret_uri = await add_juju_secret(
            ops_test,
            "azure-storage",
            "iamsecret",
            {"secret-key": azure_credentials.secret_key},
        )
        await set_azure_credentials(
            ops_test, secret_uri=secret_uri, application_name="azure-storage"
        )

    if cos:
        with ops_test.model_context(COS_ALIAS) as cos_model:
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
        apps=applications,
        timeout=2500,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    yield applications
