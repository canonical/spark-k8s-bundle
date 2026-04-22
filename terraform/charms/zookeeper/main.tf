# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "zookeeper" {
  name       = var.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "zookeeper-k8s"
    base     = var.base
    channel  = var.channel
    revision = var.revision
  }

  config = var.config

  storage_directives = {
    zookeeper = var.storage_size
  }

  resources   = var.resources
  units       = var.units
  constraints = var.constraints
}
