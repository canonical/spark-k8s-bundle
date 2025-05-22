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
from typing import Generator, Iterable, cast

import httpx
import jubilant
import pytest
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
    deploy_bundle,
    deploy_bundle_terraform,
    deploy_bundle_yaml,
    deploy_bundle_yaml_azure_storage,
    local_tmp_folder,
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


@pytest.fixture(scope="module")
def juju(request: pytest.FixtureRequest):
    keep_models = bool(request.config.getoption("--keep-models"))
    model = request.config.getoption("--model")

    if model is None:
        with jubilant.temp_model(keep=keep_models) as juju:
            juju.wait_timeout = 30 * 60
            juju.model_config({"update-status-hook-interval": "60s"})
            yield juju  # run the test

            if request.session.testsfailed:
                log = juju.debug_log(limit=50)
                print(log, end="")
                logger.info(juju.cli("status"))

    else:
        juju = jubilant.Juju()
        juju.model = str(model)
        juju.wait_timeout = 30 * 60
        try:
            juju.status()
        except jubilant.CLIError:
            juju.add_model(str(model))

        juju.model_config({"update-status-hook-interval": "60s"})
        yield juju

        if request.session.testsfailed:
            log = juju.debug_log(limit=50)
            print(log, end="")
            logger.info(juju.cli("status"))


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
def cos(cos_model: str, backend: str):
    """
    Deploy COS bundle depending upon the value of cos_model fixture, and yield its value.
    """

    cos = jubilant.Juju()
    cos.model = cos_model
    try:
        cos.status()
    except jubilant.CLIError:
        cos_exists = False
    else:
        cos_exists = True

    if cos_model and not cos_exists and backend == "yaml":
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

        yield cos_model

    else:
        # try:
        #     cos.add_model(COS_ALIAS)
        # except jubilant.CLIError:
        #     # already exists
        #     pass
        yield cos_model


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


def spark_bundle_with_s3(juju: jubilant.Juju, credentials, bucket, bundle, cos):
    """Deploy all applications in the Kyuubi bundle, wait for all of them to be active,
    and finally yield a list of the names of the applications that were deployed.
    """

    if isinstance(bundle, Bundle):
        applications = deploy_bundle_yaml(bundle, bucket, cos, juju)

    else:
        applications = deploy_bundle_terraform(
            bundle,
            bucket,
            cos,
            juju,
            storage_backend="s3",
        )

    if "s3" in applications:
        juju.wait(lambda status: jubilant.all_agents_idle(status, "s3"))

        set_s3_credentials(juju, credentials)

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
            status, *list(set(applications) - set(COS_APPS))
        ),
        timeout=1800,
        delay=10,
    )
    return applications


def spark_bundle_with_azure_storage(
    juju: jubilant.Juju,
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
        applications = deploy_bundle_yaml_azure_storage(
            bundle_with_azure_storage, container, cos, juju
        )

    else:
        applications = deploy_bundle_terraform(
            bundle_with_azure_storage,
            container,
            cos,
            juju,
            storage_backend="azure",
        )

    if "azure-storage" in applications:
        secret_uri = juju.add_secret(
            "iamsecret", {"secret-key": azure_credentials.secret_key}
        )
        juju.cli("grant-secret", secret_uri, "azure-storage")
        juju.config("azure-storage", {"credentials": secret_uri})

    if cos:
        with track_model(COS_ALIAS) as cos_model:
            logger.info("Waiting for COS deployment to settle down")
            cos_model.wait(
                lambda status: jubilant.all_active(status, *COS_APPS),
                timeout=1800,
                delay=10,
            )

    logger.info("Waiting for spark deployment to settle down")
    juju.wait(
        lambda status: jubilant.all_active(
            status, *list(set(applications) - set(COS_APPS))
        ),
        timeout=1800,
        delay=10,
    )

    return applications


@pytest.fixture(scope="module")
def spark_bundle(request, storage_backend, cos, juju: jubilant.Juju):
    if storage_backend == "s3":
        credentials = request.getfixturevalue("credentials")
        bucket = request.getfixturevalue("bucket")
        bundle = request.getfixturevalue("bundle")
        return spark_bundle_with_s3(juju, credentials, bucket, bundle, cos)
    elif storage_backend == "azure":
        azure_credentials = request.getfixturevalue("azure_credentials")
        container = request.getfixturevalue("container")
        bundle_with_azure_storage = request.getfixturevalue("bundle_with_azure_storage")
        return spark_bundle_with_azure_storage(
            juju, azure_credentials, container, bundle_with_azure_storage, cos
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
