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
