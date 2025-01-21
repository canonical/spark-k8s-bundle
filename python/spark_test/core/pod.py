# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
import json
import subprocess
from functools import cached_property
from pathlib import Path
from typing import Dict, Iterator, List

import lightkube
from lightkube import Client, KubeConfig

from spark_test import BINS, PKG_DIR


def get_kube_config(kubeconfig_file: Path | None) -> KubeConfig:
    """Return the KubeConfig from a provided filename.

    Args:
        kubeconfig_file: Path of the kubeconfig file. If not provided, the
            default from the environment will be taken.

    Returns:
        lightkube.KubeConfig instance
    """
    if kubeconfig_file.exists():
        return KubeConfig.from_file(kubeconfig_file.absolute())
    else:
        return KubeConfig.from_env()


class Pod:
    """Object representing a running Pod on K8s."""

    def __init__(self, pod_name: str, namespace: str, kubeconfig_file: Path | None):
        """Create an instance of Pod class.

        Args:
            pod_name: name of the pod on K8s
            namespace: namespace that the pod belongs to
            kubeconfig_file: kubeconfig filepath
        """
        self.pod_name = pod_name
        self.namespace = namespace
        self.kubeconfig_file = kubeconfig_file

    def write(self, filename):
        with open(filename, "w") as fid:
            json.dump(
                {
                    "pod_name": self.pod_name,
                    "namespace": self.namespace,
                    "kubeconfig_file": str(self.kubeconfig_file),
                },
                fid,
            )

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as fid:
            data = json.load(fid)
        data["kubeconfig_file"] = Path(data["kubeconfig_file"])
        return cls(**data)

    def exec(self, cmd: List[str], envs: Dict[str, str] | None = None):
        """Execute a command on the pod.

        Args:
            cmd: list of strings representing the command to be executed
            envs: dictionary representing environment variables to be used
                in the execution

        Returns:
            output of the command
        """

        kubeconfig_line = (
            [
                "--kubeconfig",
                str(self.kubeconfig_file.absolute()),
            ]
            if self.kubeconfig_file
            else []
        )

        env_args = (["env"] + [f'{k}="{v}"' for k, v in envs.items()]) if envs else []
        cmd_line = " ".join(cmd)

        return subprocess.check_output(
            ["kubectl"]
            + kubeconfig_line
            + ["-n", self.namespace, "exec", self.pod_name, "--"]
            + env_args
            + ["/bin/bash", "-c", cmd_line]
        )

    @classmethod
    def create(
        cls,
        pod_name: str,
        namespace: str,
        service_account: str,
        spark_image: str,
        kubeconfig_file: Path | None,
    ):
        """Create a pod.

        Args:
            pod_name: pod name
            namespace: name of the namespace
            service_account: name of the service account to be used. Use "admin"
                for using context from a local kubeconfig file
            spark_image: base image to be used for the container/pod
            kubeconfig_file: path to the local kubeconfig file

        Returns:
             an instance of a Pod class
        """
        if service_account == "admin":

            if not kubeconfig_file:
                raise ValueError(
                    "A Kubeconfig admin file must be provided for spawning "
                    "admin pods"
                )

            subprocess.check_output(
                [
                    f"{BINS.relative_to(PKG_DIR) / 'pod.sh'}",
                    "create",
                    pod_name,
                    namespace,
                    "admin",
                    spark_image,
                    kubeconfig_file,
                ],
                cwd=PKG_DIR,
            )
        else:
            subprocess.check_output(
                [
                    f"{BINS.relative_to(PKG_DIR) / 'pod.sh'}",
                    "create",
                    pod_name,
                    namespace,
                    "normal",
                    spark_image,
                    service_account,
                ],
                cwd=PKG_DIR,
            )

        return Pod(pod_name, namespace, kubeconfig_file)

    @cached_property
    def client(self) -> Client:
        """Return lightkube.Client instance used by the backend."""
        kubeconfig = get_kube_config(self.kubeconfig_file)
        return Client(config=kubeconfig)

    def logs(self) -> Iterator[str]:
        """Return the logs of the pod."""
        return (
            line
            for line in self.client.log(name=self.pod_name, namespace=self.namespace)
        )

    @property
    def metadata(self):
        """Return the metadata of the pod."""
        return self.client.get(
            lightkube.resources.core_v1.Pod,
            name=self.pod_name,
            namespace=self.namespace,
        ).metadata

    @property
    def labels(self) -> Dict[str, str]:
        """Return the labels of the pod."""
        return self.client.get(
            lightkube.resources.core_v1.Pod,
            name=self.pod_name,
            namespace=self.namespace,
        ).metadata.labels

    def delete(self):
        """Delete the current pod."""
        subprocess.check_output(
            [
                f"{BINS.relative_to(PKG_DIR) / 'pod.sh'}",
                "teardown",
                self.pod_name,
                self.namespace,
            ],
            cwd=PKG_DIR,
        )
