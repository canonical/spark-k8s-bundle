import os
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration", action="store_true", help="flag to enable integration tests"
    )
    parser.addoption(
        "--bundle",
        required=False,
        help="Path to a bundle to be used in integration tests",
    )


@pytest.fixture
def bundle(request):
    IE_TEST_DIR = Path(os.path.dirname(__file__))

    BUNDLE_FILE = IE_TEST_DIR / ".." / ".." / ".." / "releases" / "3.4" / "bundle.yaml.j2"

    bundle = (
        Path(file) if (file := request.config.getoption("--bundle")) else None
    ) or BUNDLE_FILE

    if not bundle.exists():
        raise FileNotFoundError("Expected a 'bundle.yaml' to be present")

    return bundle


@pytest.fixture
def integration_test(request):
    env_flag = bool(int(os.environ.get("IE_TEST", "0")))
    cli_flag = request.config.getoption("--integration")

    if not env_flag and not cli_flag:
        pytest.skip(
            reason="Integration test, to be skipped when running unittests",
        )
