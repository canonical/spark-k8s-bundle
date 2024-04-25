import os
from pathlib import Path

import pytest

from tests import BUNDLE_FILE, RELEASE_DIR

from .helpers import Bundle


def pytest_addoption(parser):
    parser.addoption(
        "--integration", action="store_true", help="flag to enable integration tests"
    )
    parser.addoption(
        "--bundle",
        required=False,
        help="Path to a bundle to be used in integration tests",
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


@pytest.fixture(scope="module")
def cos_model(request) -> None | str:
    return request.config.getoption("--cos-model")


@pytest.fixture(scope="module")
def bundle(request, cos_model) -> Bundle[Path]:
    bundle = (
        Path(file) if (file := request.config.getoption("--bundle")) else None
    ) or BUNDLE_FILE

    overlays = (
        [Path(file) for file in files]
        if (files := request.config.getoption("--overlay"))
        else (
            [RELEASE_DIR / "resources" / "overlays" / "cos-integration.yaml.j2"]
            if cos_model
            else []
        )
    )

    for file in overlays + [bundle]:
        if not file.exists():
            raise FileNotFoundError(file.absolute())

    return Bundle(main=bundle, overlays=overlays)


@pytest.fixture
def integration_test(request):
    env_flag = bool(int(os.environ.get("IE_TEST", "0")))
    cli_flag = request.config.getoption("--integration")

    if not env_flag and not cli_flag:
        pytest.skip(
            reason="Integration test, to be skipped when running unittests",
        )
