# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "kyuubi" {
  name       = var.kyuubi.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "kyuubi-k8s"
    base     = var.kyuubi.base
    channel  = "${var.kyuubi.track}/${var.risk}"
    revision = var.kyuubi.revision
  }

  config      = var.kyuubi.config
  units       = var.kyuubi.units
  constraints = var.kyuubi.constraints
  resources   = var.kyuubi.resources
  trust       = true
}
