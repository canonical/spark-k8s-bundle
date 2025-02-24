# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">=1.7.3"

  required_providers {
    juju = {
      version = "~> 0.14.0"
      source  = "juju/juju"
    }
  }
}

provider "juju" {}
