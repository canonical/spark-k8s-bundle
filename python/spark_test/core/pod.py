import subprocess
from pathlib import Path
from typing import Dict, List

from spark_test import BINS, PKG_DIR


class Pod:

    def __init__(self, pod_name: str, namespace: str, kubeconfig_file: Path | None):
        self.pod_name = pod_name
        self.namespace = namespace
        self.kubeconfig_file = kubeconfig_file

    def exec(self, cmd: List[str], envs: Dict[str, str] | None = None):
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
        kubeconfig_file: Path | None,
    ):
        """Create a pod.

        Args:
            pod_name: pod name
            namespace: name of the namespace
            service_account: name of the service account to be used. Use "admin"
                for using context from a local kubeconfig file
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
                    service_account,
                ],
                cwd=PKG_DIR,
            )

        return Pod(pod_name, namespace, kubeconfig_file)

    def delete(self):
        subprocess.check_output(
            [
                f"{BINS.relative_to(PKG_DIR) / 'pod.sh'}",
                "teardown",
                self.pod_name,
                self.namespace,
            ],
            cwd=PKG_DIR,
        )
