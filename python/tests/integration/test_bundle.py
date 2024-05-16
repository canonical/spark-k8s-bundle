#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import pytest
from pytest_operator.plugin import OpsTest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace
from spark_test.fixtures.s3 import bucket, credentials
from spark_test.fixtures.service_account import registry, service_account

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def bucket_name():
    return "spark-bucket"


@pytest.fixture
def pod_name():
    return "my-testpod"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(ops_test, kyuubi_bundle):
    """Test whether the bundle has deployed successfully."""
    async for applications in kyuubi_bundle:
        for app_name in applications:
            assert ops_test.model.applications[app_name].status == "active"
