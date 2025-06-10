from pathlib import Path
import pytest
import logging
import jubilant

logger = logging.getLogger(__name__)


def test_terraform(spark_bundle):
    applications = spark_bundle
    logger.info(f"Deployed these applications: {applications}")


def test_after_destroy():
    logger.info("The TF bundle has been destroyed")
    import time

    time.sleep(2 * 60)
