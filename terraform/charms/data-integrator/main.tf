# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "data_integrator" {
  name       = var.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "data-integrator"
    channel  = var.channel
    revision = var.revision
  }

  config      = var.config
  units       = var.units
  constraints = var.constraints
}
