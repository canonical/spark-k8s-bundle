# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  application = {
    charm              = "kyuubi-k8s"
    base               = var.kyuubi.base
    track              = var.kyuubi.track
    constraints        = var.kyuubi.constraints
    architecture       = try(split(" ", split("arch=", var.kyuubi.constraints)[1])[0], "amd64")
    revision_override  = var.kyuubi.revision
    resource_overrides = var.kyuubi.resources != null ? var.kyuubi.resources : {}
  }

  resolved_application = merge(
    local.application,
    {
      channel  = "${local.application.track}/${var.risk}"
      revision = coalesce(local.application.revision_override, data.juju_charm.kyuubi.revision)
      resources = merge(
        {
          for resource_name, resource_revision in data.juju_charm.kyuubi.resources :
          resource_name => tonumber(resource_revision)
        },
        local.application.resource_overrides
      )
    }
  )
}

data "juju_charm" "kyuubi" {
  charm        = local.application.charm
  base         = local.application.base
  channel      = "${local.application.track}/${var.risk}"
  architecture = local.application.architecture
  revision     = local.application.revision_override
}
