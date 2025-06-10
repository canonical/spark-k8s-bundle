# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from __future__ import annotations

import contextlib
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
from typing import Generator, cast

import httpx
import jubilant
import pytest
from spark8t.domain import PropertyFile

from spark_test.core.azure_storage import Container
from spark_test.core.bundle import BundleBackendEnum
from spark_test.core.bundle.terraform import TerraformBackend
from spark_test.core.bundle.yaml import YamlBackend
from spark_test.core.s3 import Bucket
from spark_test.fixtures.azure_storage import azure_credentials, container  # noqa
from spark_test.fixtures.pod import spark_image  # noqa
from spark_test.fixtures.s3 import bucket, credentials  # noqa
from spark_test.fixtures.service_account import service_account  # noqa
from tests import RELEASE_DIR

from .helpers import (
    COS_ALIAS,
    Bundle,
    deploy_bundle,
    local_tmp_folder,
    set_s3_credentials,
)

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


def pytest_runtest_setup(item):
    if (
        "skip_if_deployed" in item.keywords
        and item.config.getoption("--no-deploy")
        and item.config.getoption("--model") is not None
    ):
        pytest.skip("Skipping deployment because --no-deploy was specified.")


def pytest_addoption(parser):
    """Add CLI options to pytest."""
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
        const="3.4.4",
        default="3.4.4",
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
    parser.addoption(
        "--model",
        action="store",
        help="Juju model to use; if not provided, a new model "
        "will be created for each test which requires one",
    )
    parser.addoption(
        "--keep-models",
        action="store_true",
        help="Keep models handled by jubilant",
    )
    parser.addoption(
        "--no-deploy",
        action="store_true",
        help="This, together with the `--model` parameter, ensures that all functions "
        "marked with the` skip_if_deployed` tag are skipped.",
    )


@pytest.fixture(scope="class")
def juju(request: pytest.FixtureRequest):
    keep_models = bool(request.config.getoption("--keep-models"))
    model = request.config.getoption("--model")

    if model is None:
        with jubilant.temp_model(keep=keep_models) as juju:
            juju.wait_timeout = 30 * 60
            yield juju
    else:
        model_name = str(model)
        juju = jubilant.Juju()
        juju.model = model_name
        juju.wait_timeout = 30 * 60
        create_model = False
        try:
            juju.status()
        except jubilant.CLIError:
            create_model = True

        if create_model:
            juju.add_model(model_name)
        yield juju

    if request.session.testsfailed:
        log = juju.debug_log(limit=50)
        print(log, end="")
        logger.info(juju.cli("status"))

    if model is not None and not keep_models:
        juju.destroy_model(model_name, destroy_storage=True, force=True)


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
    return request.config.getoption("--spark-version") or "3.4.4"


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
def namespace_name(juju: jubilant.Juju) -> str:
    return cast(str, juju.model)


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


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
def cos(cos_model: str, backend: str):
    """
    Deploy COS bundle depending upon the value of cos_model fixture, and yield its value.
    """
    if not cos_model:
        return None

    cos = jubilant.Juju()
    cos.model = cos_model
    try:
        cos.status()
        return cos_model
    except jubilant.CLIError:
        cos.add_model(COS_ALIAS)

    if backend == BundleBackendEnum.YAML.value:
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

            cos.add_model(COS_ALIAS)

            deploy_bundle(cos, cos_bundle)

            cos.offer("traefik", endpoint="ingress")
            cos.wait(lambda status: jubilant.all_active(status, "traefik"))

    return cos_model


@contextlib.contextmanager
def track_model(model: str) -> Generator[jubilant.Juju]:
    """Context manager to create a temporary model for running tests in.

    This creates a new model with a random name in the format ``jubilant-abcd1234``, and destroys
    it and its storage when the context manager exits.

    Provides a :class:`Juju` instance to operate on.

    Args:
        keep: If true, keep the created model around when the context manager exits.
        controller: Name of controller where the temporary model will be added.
    """
    juju = jubilant.Juju()
    juju.model = model
    yield juju


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


@pytest.fixture(scope="class")
def tempdir():
    with local_tmp_folder() as tmp_folder:
        yield tmp_folder


@pytest.fixture(scope="class")
def spark_bundle(
    request,
    backend,
    tempdir,
    spark_version,
    juju,
    cos,
    storage_backend,
    object_storage,
):
    short_version = ".".join(spark_version.split(".")[:2])
    release_path = RELEASE_DIR / short_version / backend

    storage_unit = (
        cast(Container, object_storage)
        if storage_backend == "azure-storage"
        else cast(Bucket, object_storage)
    )

    if backend == BundleBackendEnum.TERRAFORM.value:
        bundle = TerraformBackend(tempdir=tempdir, module_path=release_path)
        base_vars = {
            "kyuubi_user": "kyuubi-test-user",
            "model": cast(str, juju.model),
            "storage_backend": storage_backend,
            "create_model": False,
            "zookeeper_units": 1,
        }
        cos_vars = {"cos_model": cos} if cos else {}
        storage_vars = (
            {
                "azure": {
                    "storage_account": storage_unit.credentials.storage_account,
                    "container": storage_unit.container_name,
                    "secret_key": storage_unit.credentials.secret_key,
                }
            }
            if storage_backend == "azure"
            else {
                "s3": {
                    "bucket": storage_unit.bucket_name,
                    "endpoint": storage_unit.s3.meta.endpoint_url,
                }
            }
        )

    elif backend == BundleBackendEnum.YAML.value:
        bundle_file = release_path / "bundle.yaml.j2"
        overlays = (
            [release_path / "overlays" / "cos-integration.yaml.j2"] if cos else []
        )
        bundle = YamlBackend(
            model=juju.model,
            tempdir=tempdir,
            bundle_file=bundle_file,
            overlays=overlays,
        )

        base_vars = {
            "namespace": cast(str, juju.model),
            "service_account": "kyuubi-test-user",
            "zookeeper_units": 1,
        }
        cos_vars = (
            {"cos_controller": juju.status().model.controller, "cos_model": cos}
            if cos
            else {}
        )
        storage_vars = (
            {
                "storage_account": storage_unit.credentials.storage_account,
                "container": storage_unit.container_name,
            }
            if storage_backend == "azure"
            else {
                "s3_endpoint": storage_unit.s3.meta.endpoint_url,
                "bucket": storage_unit.bucket_name,
            }
        )

    else:
        raise NotImplementedError(
            f"The backend {backend} is not supported for deploying bundle."
        )

    vars = base_vars | cos_vars | storage_vars

    deployed_applications = bundle.apply(vars=vars)
    if storage_backend == "azure":
        credentials = request.getfixturevalue("azure_credentials")
        secret_uri = juju.add_secret(
            "iamsecret", {"secret-key": azure_credentials.secret_key}
        )
        juju.cli("grant-secret", secret_uri, "azure-storage")
        juju.config("azure-storage", {"credentials": secret_uri})
    else:
        credentials = request.getfixturevalue("credentials")
        juju.wait(lambda status: jubilant.all_agents_idle(status, "s3"))
        set_s3_credentials(juju, credentials=credentials)

    if cos:
        with track_model(COS_ALIAS) as cos_model:
            logger.info("Waiting for COS deployment to settle down")
            cos_model.wait(
                lambda status: jubilant.all_agents_idle(status, *COS_APPS),
                timeout=1800,
                delay=10,
            )

    logger.info("Waiting for spark deployment to settle down")
    juju.wait(
        lambda status: jubilant.all_active(
            status, *list(set(deployed_applications) - set(COS_APPS))
        ),
        timeout=1800,
        delay=10,
    )

    yield deployed_applications

    # bundle.destroy()
