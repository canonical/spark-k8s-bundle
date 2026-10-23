#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Utils module."""

import re
from typing import cast

from lightkube import Client
from lightkube.core.client import LabelSelector
from lightkube.resources.core_v1 import Pod as LightKubePod

from spark_test.core.pod import Pod

SPARK_EXECUTOR_POD_REGEX = r".*-exec-\d+"


def get_pods_by_label(
    client: Client, labels: dict[str, str], namespace: str | None = None
) -> list[Pod]:
    """Get pods matching all the given labels."""
    pods = client.list(
        LightKubePod, labels=cast(LabelSelector, labels), namespace=namespace
    )
    result = []
    for pod in pods:
        if not pod.metadata or not pod.metadata.name:
            continue
        pod_namespace = getattr(pod.metadata, "namespace", None) or namespace
        if not pod_namespace:
            continue
        result.append(
            Pod(
                pod_name=pod.metadata.name,
                namespace=pod_namespace,
                kubeconfig_file=client.config.fname,
            )
        )
    return result


def get_unit_pods(client: Client, model: str, application_name: str) -> list[Pod]:
    """Get pods belonging to a Juju application in a model."""
    return get_pods_by_label(
        client,
        labels={"app.kubernetes.io/name": application_name},
        namespace=model,
    )


def pod_has_labels(pod: Pod, labels: dict[str, str]) -> bool:
    """Check whether a pod has all the given labels."""
    pod_labels = pod.labels
    return bool(pod_labels) and all(
        pod_labels.get(key) == value for key, value in labels.items()
    )


def get_spark_drivers(
    client: Client | None = None, namespace: str = "default"
) -> list[Pod]:
    """Get Spark driver pod."""
    if client is None:
        client = Client()

    pods = []
    for pod in client.list(LightKubePod, namespace=namespace):
        assert pod.metadata is not None
        if (pod_name := pod.metadata.name) and pod_name.endswith("driver"):
            pods.append(
                Pod(
                    pod_name=pod_name,
                    namespace=namespace,
                    kubeconfig_file=client.config.fname,
                )
            )
    return pods


def get_spark_executors(
    client: Client | None = None, namespace: str = "default", prefix: str = ""
) -> list[Pod]:
    """Get Spark executor pods for a given namespace."""
    if client is None:
        client = Client()

    pods = []
    for pod in client.list(LightKubePod, namespace=namespace):
        assert pod.metadata is not None
        if (pod_name := pod.metadata.name) and re.match(
            SPARK_EXECUTOR_POD_REGEX, pod_name
        ):
            pods.append(
                Pod(
                    pod_name=pod_name,
                    namespace=namespace,
                    kubeconfig_file=client.config.fname,
                )
            )
    return pods
