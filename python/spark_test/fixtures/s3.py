import subprocess

import pytest

from spark_test import BINS, PKG_DIR
from spark_test.core.s3 import Bucket, Credentials


@pytest.fixture
def credentials():
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


@pytest.fixture
def bucket_name():
    return "s3-bucket"


@pytest.fixture
def bucket(credentials, bucket_name):
    _bucket = Bucket.create(bucket_name, credentials)

    yield _bucket

    _bucket.delete()
