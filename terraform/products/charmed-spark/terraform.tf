# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      # TODO: Unpin juju<1.5.5 when https://github.com/juju/terraform-provider-juju/pull/1298 gets merged and released
      version = ">=1.0.0,<1.5.5"
    }
  }
}
