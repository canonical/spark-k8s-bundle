# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "history_server_azure_storage" {
  model_uuid = data.juju_model.spark.id

  application {
    name     = juju_application.azure_storage.name
    endpoint = "azure-storage-credentials"
  }

  application {
    name     = var.spark_charms.history_server
    endpoint = "azure-storage-credentials"
  }
}

resource "juju_integration" "azure_storage_integration_hub" {
  model_uuid = data.juju_model.spark.id

  application {
    name     = juju_application.azure_storage.name
    endpoint = "azure-storage-credentials"
  }

  application {
    name     = var.spark_charms.integration_hub
    endpoint = "azure-storage-credentials"
  }
}
