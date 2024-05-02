#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from spark_test.core.pod import Pod
from spark_test.fixtures.k8s import kubeconfig, namespace
from spark_test.fixtures.service_account import service_account


@pytest.fixture
def pod_name():
    return "testpod"


@pytest.fixture(scope="module")
def admin_pod_name():
    return "testpod-admin"


@pytest.fixture(scope="module")
def admin_pod(kubeconfig, namespace, admin_pod_name):

    _pod = Pod.create(admin_pod_name, namespace, "admin", kubeconfig.fname)

    yield _pod

    _pod.delete()


@pytest.fixture
def pod(kubeconfig, namespace, pod_name, service_account):

    _pod = Pod.create(
        pod_name, service_account.namespace, service_account.name, kubeconfig.fname
    )

    yield _pod

    _pod.delete()
