import pytest

from spark_test import RESOURCES
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod, pod_name
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import (
    iceberg_properties,
    registry,
    s3_properties,
    service_account,
    small_profile_properties,
)
from spark_test.utils import get_spark_drivers


@pytest.fixture(scope="module")
def bucket_name():
    return "spark-bucket"


@pytest.fixture(scope="module")
def namespace_name():
    return "spark-s3"


@pytest.fixture
def spark_properties(small_profile_properties, s3_properties, iceberg_properties):
    return small_profile_properties + s3_properties + iceberg_properties


def test_spark_iceberg_integration(
    pod, service_account, registry, bucket, spark_properties
):

    num_rows = 4

    bucket.upload_file(RESOURCES / "python" / "test-iceberg.py")

    registry.set_configurations(service_account.id, spark_properties)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            f"s3a://{bucket.bucket_name}/test-iceberg.py",
            "-n",
            str(num_rows),
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

    line_check = filter(
        lambda line: "Number of rows inserted:" in line, driver_pods[0].logs()
    )
    assert next(line_check)
