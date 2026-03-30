# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

locals {
  target_model_uuid = var.model_uuid != null ? var.model_uuid : data.juju_model.spark.id
}

data "juju_model" "spark" {
  name = var.model
}

resource "juju_secret" "azure_blob_storage_secret" {
  model_uuid = local.target_model_uuid
  name  = "azure_blob_storage_secret"
  value = {
    secret-key = var.azure_storage.secret_key
  }
  info = "This is the secret key for the Azure storage account"
}

resource "juju_access_secret" "azure_blob_storage_secret_access" {
  model_uuid = local.target_model_uuid
  applications = [
    juju_application.azure_storage.name
  ]
  # Use the secret_id from your secret resource or data source.
  secret_id = juju_secret.azure_blob_storage_secret.secret_id
}
