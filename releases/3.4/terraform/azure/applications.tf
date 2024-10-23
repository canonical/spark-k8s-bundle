resource "juju_secret" "azure_blob_storage_secret" {
  model = var.model
  name  = "azure_blob_storage_secret"
  value = {
    secret-key = var.azure.secret_key
  }
  info = "This is the secret key for the Azure storage account"
}

resource "juju_access_secret" "azure_blob_storage_secret_access" {
  model = var.model
  applications = [
    juju_application.azure_storage.name
  ]
  # Use the secret_id from your secret resource or data source.
  secret_id = juju_secret.azure_blob_storage_secret.secret_id
}

resource "juju_application" "azure_storage" {
  name = "azure-storage"

  model      = var.model

  charm {
    name    = "azure-storage-integrator"
    channel = "latest/edge"
    revision = 1
  }

  config = {
    container = var.azure.container
    storage-account = var.azure.storage_account
    path = var.azure.path
    connection-protocol = var.azure.protocol
    credentials = juju_secret.azure_blob_storage_secret.secret_id
  }

  units = 1

  constraints = "arch=amd64"

}
