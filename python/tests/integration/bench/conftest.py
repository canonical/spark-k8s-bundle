import shutil

import pytest


def pytest_addoption(parser):
    """Add CLI options to pytest."""
    parser.addoption(
        "--bench-sf",
        choices=[
            "sf1",
            "sf10",
            "sf30",
            "sf100",
            "sf300",
            "sf1000",
            "sf3000",
            "sf10000",
            "sf30000",
            "sf100000",
        ],
        type=str,
        help="Benchmark size factor. 'sf1' = 1GB",
        default="sf1",
    )
    parser.addoption(
        "--bench-iterations",
        default=3,
        type=int,
        help="Number of iteration for each benchmark query.",
    )
    parser.addoption(
        "--report-name",
        default="report",
        type=str,
        help="File name for the benchmark report.",
    )
    parser.addoption(
        "--kyuubi-app",
        default="kyuubi",
        type=str,
        help="Kyuubi application name.",
    )
    parser.addoption(
        "--hub-app",
        default="integration-hub",
        type=str,
        help="Integration Hub application name.",
    )


@pytest.fixture(scope="module")
def sf(request) -> str:
    """Get benchmark size factor."""
    return request.config.getoption("--bench-sf")


@pytest.fixture(scope="module")
def bench_iterations(request) -> int:
    """Get benchmark number of iterations."""
    return request.config.getoption("--bench-iterations")


@pytest.fixture(scope="module")
def report_name(request) -> str:
    """Get benchmark number of iterations."""
    return request.config.getoption("--report-name")


@pytest.fixture(scope="module")
def kyuubi(request):
    return request.config.getoption("--kyuubi-app")


@pytest.fixture(scope="module")
def hub(request):
    return request.config.getoption("--hub-app")


@pytest.fixture(scope="session")
def spark_client() -> str:
    """Check that spark-client is in path."""
    if (spark_client_path := shutil.which("spark-client")) is None:
        raise FileNotFoundError("Could not find 'spark-client' in PATH.")

    return spark_client_path
