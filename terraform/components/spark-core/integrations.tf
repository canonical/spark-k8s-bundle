# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

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

resource "juju_integration" "integration_hub_service_mesh" {
  count      = var.service_mesh != null ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.integration_hub.name
    endpoint = "service-mesh"
  }

  application {
    name      = var.service_mesh.kind == "endpoint" ? var.service_mesh.name : null
    endpoint  = var.service_mesh.kind == "endpoint" ? var.service_mesh.endpoint : null
    offer_url = var.service_mesh.kind == "offer" ? var.service_mesh.url : null
  }
}

resource "juju_integration" "history_server_service_mesh" {
  count      = var.service_mesh != null ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.history_server.name
    endpoint = "service-mesh"
  }

  application {
    name      = var.service_mesh.kind == "endpoint" ? var.service_mesh.name : null
    endpoint  = var.service_mesh.kind == "endpoint" ? var.service_mesh.endpoint : null
    offer_url = var.service_mesh.kind == "offer" ? var.service_mesh.url : null
  }
}

resource "juju_integration" "history_server_ingress" {
  count      = var.ingress != null ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.history_server.name
    endpoint = "ingress"
  }

  application {
    name      = var.ingress.kind == "endpoint" ? var.ingress.name : null
    endpoint  = var.ingress.kind == "endpoint" ? var.ingress.endpoint : null
    offer_url = var.ingress.kind == "offer" ? var.ingress.url : null
  }
}
