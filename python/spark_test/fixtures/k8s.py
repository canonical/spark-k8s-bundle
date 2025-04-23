#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""K8s fixtures."""

import os
import time
from pathlib import Path

import pytest
from lightkube.resources.core_v1 import Namespace
from spark8t.domain import Defaults, KubernetesResourceType
from spark8t.services import LightKube

from spark_test.core.pod import get_kube_config


@pytest.fixture(scope="session")
def kubeconfig():
    """Load kube config."""
    return get_kube_config(Path.home() / ".kube" / "config")


@pytest.fixture(scope="session")
def envs(kubeconfig):
    """Kube config environment variables."""
    kubeconfig_env = {"KUBECONFIG": f"{kubeconfig.fname}"} if kubeconfig.fname else {}

    return Defaults(dict(os.environ) | kubeconfig_env)


def _get_namespaces(interface):
    return [ns.metadata.name for ns in interface.client.list(Namespace)]


@pytest.fixture(scope="session")
def interface(envs):
    """Lightkube interface."""
    interface = LightKube(envs.kube_config, envs)
    ns_before = _get_namespaces(interface)
    yield interface
    ns_after = _get_namespaces(interface)
    for ns in set(ns_after) - set(ns_before):
        interface.client.delete(Namespace, name=ns)


@pytest.fixture(scope="module")
def namespace_name():
    """Namespace name."""
    return "spark-test"


@pytest.fixture(scope="module")
def namespace(interface, namespace_name):
    """Create namespace."""
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
