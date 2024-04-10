import pytest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import admin_pod, pod
from spark_test.fixtures.service_account import registry, service_account
from spark_test.utils import assert_logs, get_spark_driver_pods


@pytest.fixture
def pod_name():
    return "my-testpod"


@pytest.fixture
def admin_pod_name():
    return "my-testpod-admin"


@pytest.fixture
def namespace_name():
    return "spark-ns"


def test_pod_admin(admin_pod, service_account):

    output: str = admin_pod.exec(
        ["spark-client.service-account-registry", "list"]
    ).decode("utf-8")

    assert output.strip("\n") == service_account.id


def test_spark_submit(pod, service_account, registry):

    from spark8t.domain import PropertyFile

    extra_confs = PropertyFile(
        {
            "spark.kubernetes.driver.request.cores": "100m",
            "spark.kubernetes.executor.request.cores": "100m",
            "spark.kubernetes.container.image": "ghcr.io/canonical/charmed-spark:3.4-22.04_edge",
        }
    )

    registry.set_configurations(service_account.id, extra_confs)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "--class",
            "org.apache.spark.examples.SparkPi",
            "local:///opt/spark/examples/jars/spark-examples_2.12-3.4.2.jar",
            "1000",
        ]
    )

    driver_pods = get_spark_driver_pods(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

    line_check = assert_logs(
        registry.kube_interface.client,
        driver_pods[0].metadata.name,
        service_account.namespace,
        ["Pi is roughly"],
    )
    assert len(line_check) > 0
