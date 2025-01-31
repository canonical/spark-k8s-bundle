# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Service account fixtures."""

import uuid

import pytest
from spark8t.domain import PropertyFile, ServiceAccount
from spark8t.services import K8sServiceAccountRegistry


def _clearnup_registry(registry):
    [registry.delete(account.id) for account in registry.all()]


@pytest.fixture(scope="session")
def registry(interface):
    """K8s registry."""
    registry = K8sServiceAccountRegistry(interface)
    yield registry

    # _clearnup_registry(registry)


@pytest.fixture(scope="module")
def service_account(registry, namespace):
    """Create service account."""
    service_account_name = f"spark-test-{uuid.uuid4()}"

    sa = ServiceAccount(
        service_account_name, namespace, registry.kube_interface.api_server
    )

    registry.create(sa)

    yield sa

    registry.delete(sa.id)


@pytest.fixture
def small_profile_properties():
    """Small profile properties."""
    return PropertyFile(
        {
            "spark.kubernetes.driver.request.cores": "100m",
            "spark.kubernetes.executor.request.cores": "100m",
        }
    )


@pytest.fixture
def s3_properties(credentials):
    """Properties relevant to s3."""
    return PropertyFile(
        {
            "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
            "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.endpoint": f"{credentials.endpoint}",
            "spark.hadoop.fs.s3a.access.key": f"{credentials.access_key}",
            "spark.hadoop.fs.s3a.secret.key": f"{credentials.secret_key}",
        }
    )


@pytest.fixture
def azure_properties(azure_credentials, warehouse_path):
    """Properties relevant to Azure storage."""
    return PropertyFile(
        {
            f"spark.hadoop.fs.azure.account.key.{azure_credentials.storage_account}.dfs.core.windows.net": azure_credentials.secret_key,
            "spark.sql.warehouse.dir": warehouse_path,
            "spark.sql.catalog.local.warehouse": warehouse_path,
        }
    )


@pytest.fixture
def iceberg_properties(warehouse_path):
    """Properties relevant to Iceberg."""
    return PropertyFile(
        {
            "spark.jars.ivy": "/tmp",
            "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            "spark.sql.catalog.spark_catalog": "org.apache.iceberg.spark.SparkSessionCatalog",
            "spark.sql.catalog.spark_catalog.type": "hive",
            "spark.sql.catalog.local": "org.apache.iceberg.spark.SparkCatalog",
            "spark.sql.catalog.local.type": "hadoop",
            "spark.sql.catalog.local.warehouse": warehouse_path,  # f"s3a://{bucket.bucket_name}/warehouse",
            "spark.sql.defaultCatalog": "local",
        }
    )
