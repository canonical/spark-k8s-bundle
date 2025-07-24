# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "kyuubi_metastore" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.metastore.name
    endpoint = "database"
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }
}

resource "juju_integration" "kyuubi_users" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.kyuubi_users.name
    endpoint = "database"
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "auth-db"
  }
}

resource "juju_integration" "kyuubi_service_account" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.kyuubi.name
    endpoint = "spark-service-account"
  }

  application {
    name     = juju_application.integration_hub.name
    endpoint = "spark-service-account"
  }
}

resource "juju_integration" "kyuubi_zookeeper" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.zookeeper.name
    endpoint = "zookeeper"
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "zookeeper"
  }
}

resource "juju_integration" "kyuubi_tls" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.kyuubi.name
    endpoint = "certificates"
  }

  application {
    name     = var.tls_app_name
    endpoint = var.tls_certificates_endpoint
  }
}

resource "juju_integration" "kyuubi_data_integrator" {
  model = data.juju_model.spark.name

  application {
    name     = juju_application.kyuubi.name
    endpoint = "jdbc"
  }

  application {
    name     = juju_application.data_integrator.name
    endpoint = "kyuubi"
  }
}

