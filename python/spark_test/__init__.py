#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""spark_test module."""

import os
from pathlib import Path

PKG_DIR = Path(os.path.dirname(__file__))

RESOURCES = PKG_DIR / "resources"

BINS = RESOURCES / "bin"
