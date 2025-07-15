#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

import jubilant
import pytest
from unittest.mock import patch

logger = logging.getLogger(__name__)


@pytest.mark.skip_if_deployed
def test_deploy_bundle(spark_bundle: list[str]) -> None:
    """Deploy bundle."""
    deployed_applications = spark_bundle
    logger.info(f"Deployed applications: {deployed_applications}")


def test_active_status(juju: jubilant.Juju, cos: str) -> None:
    """Test whether the bundle has deployed successfully."""
    juju.wait(
        lambda status: jubilant.all_active(status) and jubilant.all_agents_idle(status),
        delay=5,
    )
    if cos:
        with patch.object(juju, "model", "cos"):
            juju.wait(jubilant.all_agents_idle, error=jubilant.any_error)
