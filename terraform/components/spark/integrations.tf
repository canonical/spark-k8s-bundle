# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "kyuubi_metastore" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }

  application {
    name      = var.metastore.kind == "endpoint" ? var.metastore.name : null
    endpoint  = var.metastore.kind == "endpoint" ? var.metastore.endpoint : null
    offer_url = var.metastore.kind == "offer" ? var.metastore.url : null
  }
}

resource "juju_integration" "kyuubi_users_db" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "auth-db"
  }

  application {
    name      = var.users_db.kind == "endpoint" ? var.users_db.name : null
    endpoint  = var.users_db.kind == "endpoint" ? var.users_db.endpoint : null
    offer_url = var.users_db.kind == "offer" ? var.users_db.url : null
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
    name      = var.zookeeper.kind == "endpoint" ? var.zookeeper.name : null
    endpoint  = var.zookeeper.kind == "endpoint" ? var.zookeeper.endpoint : null
    offer_url = var.zookeeper.kind == "offer" ? var.zookeeper.url : null
  }
}

resource "juju_integration" "kyuubi_certificates" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "certificates"
  }

  application {
    name      = var.certificates.kind == "endpoint" ? var.certificates.name : null
    endpoint  = var.certificates.kind == "endpoint" ? var.certificates.endpoint : null
    offer_url = var.certificates.kind == "offer" ? var.certificates.url : null
  }
}

resource "juju_integration" "kyuubi_data_integrator" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.kyuubi.name
    endpoint = "jdbc"
  }

  application {
    name      = var.data_integrator.kind == "endpoint" ? var.data_integrator.name : null
    endpoint  = var.data_integrator.kind == "endpoint" ? var.data_integrator.endpoint : null
    offer_url = var.data_integrator.kind == "offer" ? var.data_integrator.url : null
  }
}

resource "juju_integration" "integration_hub_object_storage" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.integration_hub.name
    endpoint = var.object_storage_interface
  }

  application {

    name      = var.object_storage.kind == "endpoint" ? var.object_storage.name : null
    endpoint  = var.object_storage.kind == "endpoint" ? var.object_storage.endpoint : null
    offer_url = var.object_storage.kind == "offer" ? var.object_storage.url : null
  }
}

resource "juju_integration" "history_server_object_storage" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.history_server.name
    endpoint = var.object_storage_interface
  }

  application {
    name      = var.object_storage.kind == "endpoint" ? var.object_storage.name : null
    endpoint  = var.object_storage.kind == "endpoint" ? var.object_storage.endpoint : null
    offer_url = var.object_storage.kind == "offer" ? var.object_storage.url : null
  }
}
