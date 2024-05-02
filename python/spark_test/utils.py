#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import List

from lightkube import Client
from lightkube.resources.core_v1 import Pod as LightKubePod

from spark_test.core.pod import Pod


def get_spark_drivers(client: Client, namespace: str) -> List[Pod]:
    return [
        Pod(
            pod_name=pod.metadata.name,
            namespace=namespace,
            kubeconfig_file=client.config.fname,
        )
        for pod in client.list(LightKubePod, namespace=namespace)
        if pod.metadata.name.endswith("driver")
    ]
