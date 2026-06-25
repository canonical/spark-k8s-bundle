# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name       = var.history_server.app_name
  model_uuid = var.model_uuid

  charm {
    name     = local.resolved_applications.history_server.charm
    base     = local.resolved_applications.history_server.base
    channel  = local.resolved_applications.history_server.channel
    revision = local.resolved_applications.history_server.revision
  }

  config      = var.history_server.config
  constraints = local.resolved_applications.history_server.constraints
  resources   = local.resolved_applications.history_server.resources
  units       = var.history_server.units
}

resource "juju_application" "integration_hub" {
  name       = var.integration_hub.app_name
  model_uuid = var.model_uuid

  charm {
    name     = local.resolved_applications.integration_hub.charm
    base     = local.resolved_applications.integration_hub.base
    channel  = local.resolved_applications.integration_hub.channel
    revision = local.resolved_applications.integration_hub.revision
  }

  config      = var.integration_hub.config
  constraints = local.resolved_applications.integration_hub.constraints
  resources   = local.resolved_applications.integration_hub.resources
  trust       = true
  units       = var.integration_hub.units
}
