#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""S3 fixtures."""

import subprocess
import uuid

import pytest

from spark_test import BINS, PKG_DIR
from spark_test.core.s3 import Bucket, Credentials


@pytest.fixture(scope="session")
def credentials():
    """S3 credentials."""
    output = subprocess.check_output(
        [f"{BINS.relative_to(PKG_DIR) / 's3.sh'}", "create"], cwd=PKG_DIR
    )

    raw_data = {
        key_value[0]: key_value[1]
        for pair in output.decode("utf-8").strip("\n").split(",")
        if (key_value := pair.split(":"))
    }

    yield Credentials(**raw_data)

    output = subprocess.check_output(
        [f"{BINS.relative_to(PKG_DIR) / 's3.sh'}", "teardown"], cwd=PKG_DIR
    )


@pytest.fixture(scope="module")
def bucket_name():
    """Bucket name."""
    return f"s3-bucket-{uuid.uuid4()}"


@pytest.fixture(scope="module")
def bucket(credentials, bucket_name, request):
    """Get or create bucket."""
    try:
        _bucket = Bucket.create(bucket_name, credentials)
        _bucket.init()
    except FileExistsError:
        _bucket = Bucket.get(bucket_name, credentials)

    yield _bucket

    keep_models = bool(request.config.getoption("--keep-models"))
    if not keep_models:
        _bucket.delete()
