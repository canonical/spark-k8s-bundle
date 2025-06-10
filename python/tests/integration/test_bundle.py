#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import jubilant
import pytest

logger = logging.getLogger(__name__)


class TestBundle:
    @pytest.mark.skip_if_deployed
    def test_deploy_bundle(self, spark_bundle):
        """Deploy bundle."""
        deployed_applications = spark_bundle
        logger.info(f"Deployed applications: {deployed_applications}")

    def test_active_status(self, juju: jubilant.Juju):
        """Test whether the bundle has deployed successfully."""
        juju.wait(jubilant.all_active)
