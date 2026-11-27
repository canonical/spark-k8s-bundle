import argparse
import shutil

import pytest

from ._support import parse_query_list, parse_spark_conf


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
    parser.addoption(
        "--bench-ambient",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Configurable benchmark: run with Istio ambient mesh enabled or not. "
        "The model name comes from --istio-system-model (default 'istio-system').",
    )
    parser.addoption(
        "--bench-cos",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Configurable benchmark: run with COS enabled or not. "
        "The model name comes from --cos-model (default 'cos').",
    )
    parser.addoption(
        "--bench-exclude-queries",
        type=parse_query_list,
        default=[],
        help="Comma-separated TPC-H query numbers (1-22) to exclude, e.g. 5,9,21.",
    )
    parser.addoption(
        "--bench-runs",
        type=int,
        default=3,
        help="Number of timed runs of each query (configurable benchmark).",
    )
    parser.addoption(
        "--bench-warmup",
        type=int,
        default=0,
        help="Number of discarded warm-up rounds before the timed runs.",
    )
    parser.addoption(
        "--bench-output-dir",
        default="bench-reports",
        type=str,
        help="Directory in which the '--report-name' report directory is created.",
    )
    parser.addoption(
        "--bench-overwrite",
        action="store_true",
        help="Replace the report directory if it already exists.",
    )
    parser.addoption(
        "--bench-spark-conf",
        action="append",
        type=parse_spark_conf,
        default=[],
        metavar="KEY=VALUE",
        help="Extra Spark/Kyuubi session configuration (repeatable). "
        "Overrides the benchmark defaults.",
    )
    parser.addoption(
        "--bench-query-timeout",
        type=int,
        default=3600,
        help="Per-query timeout in seconds; the query is cancelled and recorded as "
        "failed. Checked on Kyuubi status polls, so it can overrun by up to ~5 s.",
    )
    parser.addoption(
        "--bench-cleanup",
        action="store_true",
        help="Drop the benchmark tables and database created by this run.",
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
def cos_model(request) -> str:
    """COS model name; '--bench-cos' selects it, falling back to '--cos-model'."""
    bench_cos = request.config.getoption("--bench-cos")
    name = request.config.getoption("--cos-model")
    if bench_cos is None:
        return name
    if bench_cos:
        return name or "cos"
    if name:
        raise pytest.UsageError("--no-bench-cos conflicts with --cos-model")
    return ""


@pytest.fixture(scope="module")
def istio_system_model(request) -> str:
    """Istio model name; '--bench-ambient' selects it, falling back to the option."""
    bench_ambient = request.config.getoption("--bench-ambient")
    name = request.config.getoption("--istio-system-model")
    if bench_ambient is None:
        return name
    if bench_ambient:
        return name or "istio-system"
    if name:
        raise pytest.UsageError("--no-bench-ambient conflicts with --istio-system-model")
    return ""


@pytest.fixture(scope="module")
def kyuubi(request):
    return request.config.getoption("--kyuubi-app")


@pytest.fixture(scope="module")
def hub(request):
    return request.config.getoption("--hub-app")


@pytest.fixture(scope="session")
def service_account_registry() -> str:
    """Find the service-account-registry command provided by the spark-client snap."""
    command = "spark-client.service-account-registry"
    if (command_path := shutil.which(command)) is None:
        raise FileNotFoundError(f"Could not find '{command}' in PATH.")

    return command_path
