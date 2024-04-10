from typing import List

from lightkube import Client
from lightkube.resources.core_v1 import Pod


def get_spark_driver_pods(client: Client, namespace: str) -> List[Pod]:
    return [
        pod
        for pod in client.list(Pod, namespace=namespace)
        if pod.metadata.name.endswith("driver")
    ]


def assert_logs(
    client: Client, pod_name: str, namespace: str, patterns: List[str]
) -> List[str]:
    lines = [
        line
        for line in client.log(name=pod_name, namespace=namespace)
        if any(pattern in line for pattern in patterns)
    ]
    return lines
