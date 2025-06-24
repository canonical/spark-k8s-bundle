# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">=1.7.3"

  required_providers {
    juju = {
      # Pin the version to <0.20 because 0.20.0 introduces some breaking changes
      # in `juju_offer` resource.
      # See: https://github.com/juju/terraform-provider-juju/issues/780
      version = ">=0.16.0, <0.20"
      source  = "juju/juju"
    }
  }
}
