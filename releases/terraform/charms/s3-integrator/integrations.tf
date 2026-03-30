# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "s3_history_server" {
  model_uuid = data.juju_model.spark.id

  application {
    name     = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name     = var.spark_charms.history_server
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_integration_hub" {
  model_uuid = data.juju_model.spark.id

  application {
    name     = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name     = var.spark_charms.integration_hub
    endpoint = "s3-credentials"
  }
}
