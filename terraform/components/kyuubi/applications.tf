# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "kyuubi" {
  name       = var.kyuubi.app_name
  model_uuid = var.model_uuid

  charm {
    name     = local.resolved_application.charm
    base     = local.resolved_application.base
    channel  = local.resolved_application.channel
    revision = local.resolved_application.revision
  }

  config      = var.kyuubi.config
  units       = var.kyuubi.units
  constraints = local.resolved_application.constraints
  resources   = local.resolved_application.resources
  trust       = true
}
