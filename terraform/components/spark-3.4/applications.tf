# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name       = var.history_server.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-history-server-k8s"
    channel  = var.history_server.channel
    revision = var.history_server.revision != null ? var.history_server.revision : local.revisions.history_server
  }

  config      = var.history_server.config
  constraints = var.history_server.constraints
  resources = merge({
    spark-history-server-image = local.images.history_server
    },
    var.history_server.resources == null ? {} : var.history_server.resources
  )
  units = var.history_server.units
}

resource "juju_application" "integration_hub" {
  name       = var.integration_hub.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = var.integration_hub.channel
    revision = var.integration_hub.revision != null ? var.integration_hub.revision : local.revisions.integration_hub
  }

  config      = var.integration_hub.config
  constraints = var.integration_hub.constraints
  resources = merge({
    integration-hub-image = local.images.integration_hub
    },
    var.integration_hub.resources == null ? {} : var.integration_hub.resources
  )
  trust = true
  units = var.integration_hub.units
}

resource "juju_application" "kyuubi" {
  name       = var.kyuubi.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "kyuubi-k8s"
    channel  = var.kyuubi.channel
    revision = var.kyuubi.revision != null ? var.kyuubi.revision : local.revisions.kyuubi
  }

  config = merge(
    {
      expose-external = "loadbalancer",
    },
    length(juju_secret.system_users_and_private_key_secret) > 0 ? {
      system-users           = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}",
      tls-client-private-key = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
    } : {},
    var.kyuubi.config
  )
  constraints = var.kyuubi.constraints
  resources = merge({
    kyuubi-image = local.images.kyuubi
    },
    var.kyuubi.resources == null ? {} : var.kyuubi.resources
  )
  trust = true
  units = var.kyuubi.units
}
