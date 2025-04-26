# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "azure_storage" {
  name  = "azure-storage"
  model = var.model
  charm {
    name     = "azure-storage-integrator"
    channel  = "latest/edge"
    revision = 12
  }
  config = {
    container           = var.azure.container
    storage-account     = var.azure.storage_account
    path                = var.azure.path
    connection-protocol = var.azure.protocol
    credentials         = "secret:${juju_secret.azure_blob_storage_secret.secret_id}"
  }
  units       = 1
  constraints = "arch=amd64"
}
