# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "kyuubi_metastore" {
  model_uuid = var.model_uuid

  application {
    name     = var.metastore_endpoint.name
    endpoint = var.metastore_endpoint.endpoint
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }
}

resource "juju_integration" "kyuubi_users" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "auth-db"
  }

  application {
    name     = var.users_db_endpoint.name
    endpoint = var.users_db_endpoint.endpoint
  }
}

resource "juju_integration" "kyuubi_service_account" {
  model_uuid = var.model_uuid

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
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "zookeeper"
  }

  application {
    name     = var.zookeeper_endpoint.name
    endpoint = var.zookeeper_endpoint.endpoint
  }
}

resource "juju_integration" "kyuubi_tls" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "certificates"
  }

  application {
    name     = var.tls_endpoint.name
    endpoint = var.tls_endpoint.endpoint
  }
}

resource "juju_integration" "kyuubi_data_integrator" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "jdbc"
  }

  application {
    name     = var.data_integrator_endpoint.name
    endpoint = var.data_integrator_endpoint.endpoint
  }
}

resource "juju_integration" "integration_hub_object_storage" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.integration_hub.name
    endpoint = var.object_storage_endpoint.endpoint
  }

  application {
    name     = var.object_storage_endpoint.name
    endpoint = var.object_storage_endpoint.endpoint
  }
}

resource "juju_integration" "history_server_object_storage" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.history_server.name
    endpoint = var.object_storage_endpoint.endpoint
  }

  application {
    name     = var.object_storage_endpoint.name
    endpoint = var.object_storage_endpoint.endpoint
  }
}
