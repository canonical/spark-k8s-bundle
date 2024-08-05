#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.pod import admin_pod, pod
from spark_test.fixtures.service_account import (
    registry, service_account, small_profile_properties
)
from spark_test.utils import get_spark_drivers


@pytest.fixture
def pod_name():
    return "my-testpod"


@pytest.fixture(scope="module")
def admin_pod_name():
    return "my-testpod-admin"


@pytest.fixture(scope="module")
def namespace_name():
    return "spark-ns"


def test_pod_admin(admin_pod, service_account):

    output: str = admin_pod.exec(
        ["spark-client.service-account-registry", "list"]
    ).decode("utf-8")

    assert output.strip("\n") == service_account.id


def test_spark_submit(
        pod, service_account, registry, version, small_profile_properties,
        image_properties
):

    extra_confs = small_profile_properties, image_properties

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
            f"local:///opt/spark/examples/jars/spark-examples_2.12-{version}.jar",
            "1000",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == 1

    line_check = filter(lambda line: "Pi is roughly" in line, driver_pods[0].logs())
    assert next(line_check)
