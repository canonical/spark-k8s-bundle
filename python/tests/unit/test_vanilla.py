#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


def test_imports():
    from spark_test import BINS  # noqa
    from spark_test.core.pod import Pod  # noqa
    from spark_test.core.s3 import Bucket  # noqa
