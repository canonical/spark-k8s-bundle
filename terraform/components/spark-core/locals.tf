# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  applications = {
    history_server = {
      charm              = "spark-history-server-k8s"
      base               = var.history_server.base
      track              = var.history_server.track
      constraints        = var.history_server.constraints
      architecture       = try(split(" ", split("arch=", var.history_server.constraints)[1])[0], "amd64")
      revision_override  = var.history_server.revision
      resource_overrides = var.history_server.resources != null ? var.history_server.resources : {}
    }
    integration_hub = {
      charm              = "spark-integration-hub-k8s"
      base               = var.integration_hub.base
      track              = var.integration_hub.track
      constraints        = var.integration_hub.constraints
      architecture       = try(split(" ", split("arch=", var.integration_hub.constraints)[1])[0], "amd64")
      revision_override  = var.integration_hub.revision
      resource_overrides = var.integration_hub.resources != null ? var.integration_hub.resources : {}
    }
  }

  resolved_applications = {
    for app_name, app in local.applications :
    app_name => merge(
      app,
      {
        channel  = "${app.track}/${var.risk}"
        revision = coalesce(app.revision_override, data.juju_charm.spark[app_name].revision)
        resources = merge(
          {
            for resource_name, resource_revision in data.juju_charm.spark[app_name].resources :
            resource_name => tonumber(resource_revision)
          },
          app.resource_overrides
        )
      }
    )
  }
}

data "juju_charm" "spark" {
  for_each = local.applications

  charm        = each.value.charm
  base         = each.value.base
  channel      = "${each.value.track}/${var.risk}"
  architecture = each.value.architecture
  revision     = each.value.revision_override
}
