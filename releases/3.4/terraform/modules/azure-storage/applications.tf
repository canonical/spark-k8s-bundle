# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "azure_storage" {
  name  = "azure-storage"
  model = var.model
  charm {
    name     = "azure-storage-integrator"
    channel  = "latest/edge"
    revision = var.azure_storage_revision
  }
  config = {
    container           = var.azure_storage.container
    storage-account     = var.azure_storage.storage_account
    path                = var.azure_storage.path
    connection-protocol = var.azure_storage.protocol
    credentials         = "secret:${juju_secret.azure_blob_storage_secret.secret_id}"
  }
  units       = 1
  constraints = "arch=amd64"
}
