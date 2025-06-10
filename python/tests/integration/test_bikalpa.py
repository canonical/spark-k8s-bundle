import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("spark_bundle")
class TestPuranoDeployment:
    def test_terraform(self, spark_bundle):
        applications = spark_bundle
        logger.info(f"Deployed these applications: {applications}")


@pytest.mark.usefixtures("spark_bundle")
class TestNewDeployment:
    def test_terraform(self, spark_bundle):
        applications = spark_bundle
        logger.info(f"Deployed these applications: {applications}")
