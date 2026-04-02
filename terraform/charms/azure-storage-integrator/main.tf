# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "azure_storage" {
  name       = var.app_name
  model_uuid = var.model_uuid
  charm {
    name     = "azure-storage-integrator"
    channel  = var.channel
    revision = var.revision
  }
  config = merge(var.config, {
    credentials = "secret:${juju_secret.azure_storage_secret.secret_id}"
  })
  units       = var.units
  constraints = var.constraints
}

# TODO: Secret creation must be handled at the product level
resource "juju_secret" "azure_storage_secret" {
  model_uuid = var.model_uuid
  name       = "azure_storage_secret"
  value = {
    secret-key = var.azure_storage_secret_key
  }
  info = "This is the secret key for the Azure storage account"
}

resource "juju_access_secret" "azure_storage_secret_access" {
  model_uuid = var.model_uuid
  applications = [
    juju_application.azure_storage.name
  ]
  secret_id = juju_secret.azure_storage_secret.secret_id
}

resource "juju_offer" "azure_storage_credentials" {
  model_uuid       = var.model_uuid
  application_name = juju_application.azure_storage.name
  endpoints        = ["azure-storage-credentials"]
}
