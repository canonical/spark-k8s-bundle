#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import pytest

from spark_test import RESOURCES
from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import pod
from spark_test.fixtures.service_account import (
    azure_properties,
    iceberg_properties,
    registry,
    s3_properties,
    service_account,
    small_profile_properties,
)
from spark_test.utils import get_spark_drivers

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def namespace_name():
    return "spark-s3"


@pytest.fixture
def warehouse_path(object_storage):
    return object_storage.get_uri("warehouse")


@pytest.fixture
def spark_properties(
    request,
    small_profile_properties,
    storage_backend,
    iceberg_properties,
    image_properties,
):
    if storage_backend == "s3":
        storage_properties = request.getfixturevalue("s3_properties")
    elif storage_backend == "azure":
        storage_properties = request.getfixturevalue("azure_properties")
    else:
        return ValueError("storage_backend argument not recognized")

    return (
        small_profile_properties
        + storage_properties
        + iceberg_properties
        + image_properties
    )


def test_cleanup_object_storage(
    pod, service_account, registry, object_storage, spark_properties
):
    if object_storage.list():
        logger.info("Cleaning up object storage")
        object_storage.cleanup()
        object_storage.init()


def test_spark_iceberg_integration(
    pod, service_account, registry, object_storage, spark_properties
):

    num_rows = 4

    object_storage.upload_file(RESOURCES / "python" / "test-iceberg.py")

    registry.set_configurations(service_account.id, spark_properties)

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            f"{object_storage.get_uri('test-iceberg.py')}",
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

    object_storage.cleanup()
