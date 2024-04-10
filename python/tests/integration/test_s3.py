import pytest

from spark_test import RESOURCES
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod, pod_name
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account
from spark_test.utils import assert_logs, get_spark_driver_pods


@pytest.fixture
def bucket_name():
    return "spark-bucket"


@pytest.fixture
def namespace_name():
    return "spark-s3"


def test_spark_iceberg_integration(pod, service_account, registry, bucket, credentials):

    num_rows = 4

    bucket.upload_file(RESOURCES / "python" / "test-iceberg.py")

    from spark8t.domain import PropertyFile

    extra_confs = PropertyFile(
        {
            "spark.kubernetes.driver.request.cores": "100m",
            "spark.kubernetes.executor.request.cores": "100m",
            "spark.kubernetes.container.image": "ghcr.io/canonical/charmed-spark:3.4-22.04_edge",
            "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
            "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.endpoint": f"{credentials.endpoint}",
            "spark.hadoop.fs.s3a.access.key": f"{credentials.access_key}",
            "spark.hadoop.fs.s3a.secret.key": f"{credentials.secret_key}",
            "spark.jars.ivy": "/tmp",
            "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark.sql.catalog.spark_catalog": "org.apache.iceberg.spark.SparkSessionCatalog",
            "spark.sql.catalog.spark_catalog.type": "hive",
            "spark.sql.catalog.local": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.local.type": "hadoop",
            "spark.sql.catalog.local.warehouse": f"s3a://{bucket.bucket_name}/warehouse",
            "spark.sql.defaultCatalog": "local",
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
            f"s3a://{bucket.bucket_name}/test-iceberg.py",
            "-n",
            str(num_rows),
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
        ["Number of rows inserted:"],
    )
    assert len(line_check) > 0
