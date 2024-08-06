# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">=1.7.3"

  required_providers {
    juju = {
      version = "~> 0.11.0"
      source  = "juju/juju"
    }
  }
}
