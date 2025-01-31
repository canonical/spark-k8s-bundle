#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import asyncio
import logging

import pytest
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


@pytest.mark.skip_if_deployed
@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest, spark_bundle):
    await spark_bundle
    await asyncio.sleep(0)  # do nothing, await deploy_cluster


@pytest.mark.abort_on_fail
async def test_active_status(ops_test):
    """Test whether the bundle has deployed successfully."""
    for app_name in ops_test.model.applications:
        assert ops_test.model.applications[app_name].status == "active"
