# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "azure_storage" {
  name       = var.app_name
  model_uuid = var.model_uuid
  charm {
    name     = "azure-storage-integrator"
    base     = var.base
    channel  = var.channel
    revision = var.revision
  }
  config      = var.config
  units       = var.units
  constraints = var.constraints
}

resource "juju_offer" "azure_storage_credentials" {
  model_uuid       = var.model_uuid
  application_name = juju_application.azure_storage.name
  endpoints        = ["azure-storage-credentials"]
}
