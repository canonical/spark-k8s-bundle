# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import shutil
import signal
import socket
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired, check_output
from typing import Iterable

import httpx
import pytest
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile

from spark_test.core.azure_storage import Credentials as AzureStorageCredentials
from spark_test.fixtures.azure_storage import azure_credentials, container  # noqa
from spark_test.fixtures.pod import spark_image  # noqa
from spark_test.fixtures.s3 import bucket, credentials  # noqa
from spark_test.fixtures.service_account import service_account  # noqa
from tests import IE_TEST_DIR

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

COS_APPS = [
    "loki",
    "grafana",
    "prometheus",
    "catalogue",
    "traefik",
    "alertmanager",
]
FORWARD_TIMEOUT_SECONDS = 10
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
        nargs="?",
        const="",
        default="",
        help="When provided, it deploys COS as well. "
        "If the model already exists, we assume COS had already been "
        "deployed.",
    )
    parser.addoption(
        "--backend",
        nargs="?",
        choices=["yaml", "terraform"],
        const="yaml",
        default="yaml",
        type=str,
        help="Which backend to use for bundle. Supported values are either "
        "yaml (default) or terraform.",
    )
    parser.addoption(
        "--spark-version",
        nargs="?",
        const="3.4.2",
        default="3.4.2",
        type=str,
        help="Which Spark version to use for bundle testing.",
    )
    parser.addoption(
        "--storage-backend",
        choices=["s3", "azure"],
        nargs="?",
        const="s3",
        default="s3",
        type=str,
        help="Which storage backend to be used. Supported values are either "
        "s3 (default) or azure.",
    )
    parser.addoption(
        "--uuid",
        default=uuid.uuid4(),
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


@pytest.fixture(scope="module")
def spark_version(request) -> str:
    """The backend which is to be used to deploy the bundle."""
    return request.config.getoption("--spark-version") or "3.4.2"


@pytest.fixture(scope="module")
def storage_backend(request) -> str:
    """The backend which is to be used to deploy the bundle."""
    return request.config.getoption("--storage-backend")


@pytest.fixture(scope="module")
def test_uuid(request) -> str:
    """The backend which is to be used to deploy the bundle."""
    return request.config.getoption("--uuid") or str(uuid.uuid4())


@pytest.fixture(scope="module")
def image_properties(spark_image):
    return PropertyFile(
        {
            "spark.kubernetes.container.image": spark_image,
        }
    )


@pytest.fixture(scope="module")
def bucket_name():
    return "spark-bucket"


@pytest.fixture(scope="module")
def container_name(test_uuid):
    return f"spark-container-{test_uuid}"


@pytest.fixture
def pod_name():
    return "my-testpod"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.fixture(scope="module")
def bundle(
    request, cos_model, backend, spark_version, tmp_path_factory
) -> Iterable[Bundle[Path] | Terraform]:
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
                [bundle.parent / "overlays" / "cos-integration.yaml.j2"]
                if cos_model
                else []
            )
        )

        for file in overlays + [bundle]:
            if not file.exists():
                raise FileNotFoundError(file.absolute())

        yield Bundle(main=bundle, overlays=overlays)


@pytest.fixture(scope="module")
def bundle_with_azure_storage(
    request, spark_version, cos_model, backend, tmp_path_factory
) -> Iterable[Bundle[Path] | Terraform]:
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
            else release_dir / "yaml" / "bundle-azure-storage.yaml.j2"
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
                [bundle.parent / "overlays" / "cos-integration.yaml.j2"]
                if cos_model
                else []
            )
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


@pytest.fixture(scope="module")
async def cos(ops_test: OpsTest, cos_model: str, backend: str):
    """
    Deploy COS bundle depending upon the value of cos_model fixture, and yield its value.
    """
    existing_models = await ops_test._controller.list_models()

    if cos_model and cos_model not in existing_models and backend == "yaml":
        base_url = (
            "https://raw.githubusercontent.com/canonical/cos-lite-bundle/main/overlays"
        )

        overlays = ["offers-overlay.yaml", "testing-overlay.yaml"]

        def create_file(path: Path, response: httpx.Response):
            path.write_text(response.content.decode("utf-8"))
            return path

        with local_tmp_folder("tmp-cos") as tmp_folder:
            logger.info(tmp_folder)

            cos_bundle = Bundle[str | Path](
                main="cos-lite",
                overlays=[
                    create_file(tmp_folder / overlay, response)
                    for overlay in overlays
                    if (response := httpx.get(f"{base_url}/{overlay}"))
                    if response.status_code == 200
                ],
            )

            await ops_test.track_model(COS_ALIAS, model_name=cos_model)

            with ops_test.model_context(COS_ALIAS) as model:
                retcode, stdout, stderr = await deploy_bundle(ops_test, cos_bundle)
                assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
                logger.info(stdout)

                await model.create_offer("traefik:ingress")

                await juju_sleep(ops_test, 15, "traefik")

        yield cos_model

        await ops_test.forget_model(cos_model)
    else:
        if cos_model:
            await ops_test.track_model(COS_ALIAS, model_name=cos_model)

        yield cos_model

        if cos_model:
            await ops_test.forget_model(cos_model)


async def spark_bundle_with_s3(ops_test: OpsTest, credentials, bucket, bundle, cos):
    """Deploy all applications in the Kyuubi bundle, wait for all of them to be active,
    and finally yield a list of the names of the applications that were deployed.
    """

    if isinstance(bundle, Bundle):
        applications = await deploy_bundle_yaml(bundle, bucket, cos, ops_test)

    else:
        applications = await deploy_bundle_terraform(
            bundle,
            bucket,
            cos,
            ops_test,
            storage_backend="s3",
        )

    if "s3" in applications:
        await ops_test.model.wait_for_idle(
            apps=["s3"], timeout=600, idle_period=30, status="blocked"
        )

        await set_s3_credentials(ops_test, credentials)

    if cos:
        with ops_test.model_context(COS_ALIAS) as cos_model:
            await cos_model.wait_for_idle(
                apps=COS_APPS,
                idle_period=60,
                timeout=3600,
                raise_on_error=False,
            )

    await ops_test.model.wait_for_idle(
        apps=list(set(applications) - set(COS_APPS)),
        timeout=3600,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    return applications


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

    if isinstance(bundle_with_azure_storage, Bundle):
        applications = await deploy_bundle_yaml_azure_storage(
            bundle_with_azure_storage, container, cos, ops_test
        )

    else:
        applications = await deploy_bundle_terraform(
            bundle_with_azure_storage,
            container,
            cos,
            ops_test,
            storage_backend="azure",
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
                apps=COS_APPS,
                idle_period=60,
                timeout=3600,
                raise_on_error=False,
            )

    await ops_test.model.wait_for_idle(
        apps=list(set(applications) - set(COS_APPS)),
        timeout=2500,
        idle_period=30,
        status="active",
        raise_on_error=False,
    )

    return applications


@pytest.fixture(scope="module")
async def spark_bundle(request, storage_backend, cos, ops_test):
    if storage_backend == "s3":
        credentials = request.getfixturevalue("credentials")
        bucket = request.getfixturevalue("bucket")
        bundle = request.getfixturevalue("bundle")
        return spark_bundle_with_s3(ops_test, credentials, bucket, bundle, cos)
    elif storage_backend == "azure":
        azure_credentials = request.getfixturevalue("azure_credentials")
        container = request.getfixturevalue("container")
        bundle_with_azure_storage = request.getfixturevalue("bundle_with_azure_storage")
        return spark_bundle_with_azure_storage(
            ops_test, azure_credentials, container, bundle_with_azure_storage, cos
        )

    else:
        raise ValueError("storage_backend argument not recognized")


@pytest.fixture(scope="module")
def object_storage(request, storage_backend):
    if storage_backend == "s3":
        return request.getfixturevalue("bucket")
    elif storage_backend == "azure":
        return request.getfixturevalue("container")
    else:
        return ValueError("storage_backend argument not recognized")


@pytest.fixture(scope="session")
def kubectl() -> str:
    """Check that kubectl is in path and is able to access the cluster."""
    if (kubectl_path := shutil.which("kubectl")) is None:
        raise FileNotFoundError("Could not find 'kubectl' in PATH.")

    check_output([kubectl_path, "get", "namespaces"])
    return kubectl_path


@pytest.fixture(scope="module")
def port_forward(kubectl: str):
    """Define a context-aware fixture to redirect a local port to a remote pod.

    This fixture is used as follows:

    ```
    def test_with_port_forwarding(
        ops_test: OpsTest,
        port_forward: PortForwarder
    ):
        with port_forward(
            pod="pod-name",
            port=8080,
            namespace="test-model"
        ):
            httpx.get("http://127.0.0.1:8080").content


    ```

    Important: the kubectl command from the microk8s snap is wrapped is such a way that
    the cleanup part does not work as expected.
    The actual port-forward process keeps running even when we forcefully terminate.
    Use the kubectl snap instead.
    """

    @contextmanager
    def _forwarder(pod: str, port: int, namespace: str, on_port: int | None = None):
        if on_port is None:
            on_port = port

        logger.info(f"Forwarding {pod} port {port} on {on_port}")
        forwarder = Popen(
            [kubectl, "port-forward", pod, f"{on_port}:{port}", "-n", namespace],
            stdout=PIPE,
            stderr=PIPE,
        )
        start = time.monotonic()

        while True:
            time.sleep(0.5)
            match forwarder.poll(), time.monotonic():
                case _, end if (end - start) > FORWARD_TIMEOUT_SECONDS:
                    # If we cannot connect within a reasonable time span,
                    # assume that it succeeded but we cannot test it using conventional methods
                    logging.warning(
                        "Cannot test port forwarding, moving on with the test anyway",
                    )
                    break

                case return_code, _ if return_code is not None:
                    try:
                        _, errs = forwarder.communicate(timeout=5)
                    except TimeoutExpired:
                        errs = "unknown error"
                    raise RuntimeError("Unable to forward the port:", errs)

                case _, _:
                    # Even if the command is actively running, we wait before the port
                    # is listening before moving on to the tests.
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        if not s.connect_ex(("127.0.0.1", port)):
                            # All good, the port is in use
                            break

        try:
            yield
        except:
            raise
        finally:
            # Stop port-forward command. If we timeout, we will get
            # a related exception to signal that we should investigate.

            forwarder.send_signal(signal.SIGINT)
            forwarder.wait(timeout=3)
            logger.info("Stopped port forwarding")

    return _forwarder
