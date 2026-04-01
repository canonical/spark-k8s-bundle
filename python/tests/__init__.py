#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import os
from pathlib import Path

IE_TEST_DIR = Path(os.path.dirname(__file__))

TERRAFORM_DIR = IE_TEST_DIR / ".." / ".." / "terraform"
PRODUCTS_DIR = TERRAFORM_DIR / "products"
