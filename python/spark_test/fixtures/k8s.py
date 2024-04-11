import os
import time
from pathlib import Path

import pytest
from lightkube import KubeConfig
from lightkube.resources.core_v1 import Namespace
from spark8t.domain import Defaults, KubernetesResourceType
from spark8t.services import LightKube


@pytest.fixture(scope="session")
def kubeconfig():
    kubeconfig_file = Path.home() / ".kube" / "config"

    if kubeconfig_file.exists():
        yield KubeConfig.from_file(kubeconfig_file.absolute())
    else:
        yield KubeConfig.from_env()


@pytest.fixture(scope="session")
def envs(kubeconfig):
    kubeconfig_env = {"KUBECONFIG": f"{kubeconfig.fname}"} if kubeconfig.fname else {}

    return Defaults(dict(os.environ) | kubeconfig_env)


def _get_namespaces(interface):
    return [ns.metadata.name for ns in interface.client.list(Namespace)]


@pytest.fixture(scope="session")
def interface(envs):
    interface = LightKube(envs.kube_config, envs)
    ns_before = _get_namespaces(interface)
    yield interface
    ns_after = _get_namespaces(interface)
    for ns in set(ns_after) - set(ns_before):
        interface.client.delete(Namespace, name=ns)


@pytest.fixture(scope="module")
def namespace_name():
    return "spark-test"


@pytest.fixture(scope="module")
def namespace(interface, namespace_name):
    print("Creating namespace")
    interface.create(KubernetesResourceType.NAMESPACE, namespace_name, None)
    yield namespace_name
    print("Deleting namespace")
    interface.delete(KubernetesResourceType.NAMESPACE, namespace_name, None)

    # To avoid racing conditions
    while namespace_name in (
        ns.metadata.name for ns in interface.client.list(Namespace)
    ):
        time.sleep(0.5)
