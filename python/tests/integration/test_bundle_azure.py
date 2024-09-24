#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import uuid

import pytest
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile

from spark_test.core.kyuubi import KyuubiClient
from spark_test.fixtures.azure_storage import azure_credentials, container

from .helpers import (
    construct_azure_resource_uri,
    get_kyuubi_credentials,
    get_postgresql_credentials,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def container_name():
    return f"spark-container-{uuid.uuid4()}"


@pytest.fixture(scope="module")
def namespace_name(ops_test: OpsTest):
    return ops_test.model_name


@pytest.fixture(scope="module")
def namespace(namespace_name):
    return namespace_name


@pytest.mark.abort_on_fail
@pytest.mark.asyncio
async def test_deploy_bundle(ops_test, spark_bundle_with_azure_storage):
    """Test whether the bundle has deployed successfully."""
    async for applications in spark_bundle_with_azure_storage:
        for app_name in applications:
            assert ops_test.model.applications[app_name].status == "active"
