# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "s3_history_server" {
  model = var.model

  application {
    name     = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name     = var.spark_charms.history_server
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_hub" {
  model = var.model

  application {
    name     = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name     = var.spark_charms.hub
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_kyuubi" {
  model = var.model

  application {
    name     = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name     = var.spark_charms.kyuubi
    endpoint = "s3-credentials"
  }
}
