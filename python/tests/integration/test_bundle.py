#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import jubilant
import pytest

from spark_test.fixtures.k8s import envs, interface, kubeconfig, namespace  # noqa
from spark_test.fixtures.s3 import bucket, credentials  # noqa
from spark_test.fixtures.service_account import registry, service_account  # noqa

logger = logging.getLogger(__name__)


@pytest.mark.skip_if_deployed
def test_deploy_bundle(spark_bundle):
    pass


def test_active_status(juju: jubilant.Juju):
    """Test whether the bundle has deployed successfully."""
    juju.wait(jubilant.all_active)
