# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name       = var.history_server.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-history-server-k8s"
    channel  = var.history_server.channel
    revision = var.history_server.revision
  }

  config      = var.history_server.config
  constraints = var.history_server.constraints
  resources   = var.history_server.resources
  units       = var.history_server.units
}

resource "juju_application" "integration_hub" {
  name       = var.integration_hub.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = var.integration_hub.channel
    revision = var.integration_hub.revision
  }

  config      = var.integration_hub.config
  constraints = var.integration_hub.constraints
  resources   = var.integration_hub.resources
  trust       = true
  units       = var.integration_hub.units
}

resource "juju_application" "kyuubi" {
  name       = var.kyuubi.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "kyuubi-k8s"
    channel  = var.kyuubi.channel
    revision = var.kyuubi.revision
  }

  config      = var.kyuubi.config
  constraints = var.kyuubi.constraints
  resources   = var.kyuubi.resources
  trust       = true
  units       = var.kyuubi.units
}
