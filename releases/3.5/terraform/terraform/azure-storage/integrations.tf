# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "history_server_azure" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.azure_storage.name
    endpoint = "azure-credentials"
  }

  application {
    name     = var.spark_charms.history_server
    endpoint = "azure-credentials"
  }
}

resource "juju_integration" "azure_hub" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.azure_storage.name
    endpoint = "azure-credentials"
  }

  application {
    name     = var.spark_charms.hub
    endpoint = "azure-credentials"
  }
}
