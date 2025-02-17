#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Utils module."""

import re

from lightkube import Client
from lightkube.resources.core_v1 import Pod as LightKubePod

from spark_test.core.pod import Pod

SPARK_EXECUTOR_POD_REGEX = r".*-exec-\d+"


def get_spark_drivers(
    client: Client | None = None, namespace: str = "default"
) -> list[Pod]:
    """Get Spark driver pod."""
    if client is None:
        client = Client()
    return [
        Pod(
            pod_name=pod.metadata.name,
            namespace=namespace,
            kubeconfig_file=client.config.fname,
        )
        for pod in client.list(LightKubePod, namespace=namespace)
        if pod.metadata.name.endswith("driver")
    ]


def get_spark_executors(
    client: Client | None = None, namespace: str = "default", prefix: str = ""
) -> list[Pod]:
    """Get Spark executor pods for a given namespace."""
    if client is None:
        client = Client()
    return [
        Pod(
            pod_name=pod.metadata.name,
            namespace=namespace,
            kubeconfig_file=client.config.fname,
        )
        for pod in client.list(LightKubePod, namespace=namespace)
        if re.match(SPARK_EXECUTOR_POD_REGEX, pod.metadata.name)
        and pod.metadata.name.startswith(prefix)
    ]
