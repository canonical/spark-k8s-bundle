# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  service_mesh_enabled    = var.service_mesh_mode != "disabled"
  managed_istio           = var.service_mesh_mode == "managed"
  model_uuid              = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid
  istio_system_model_uuid = length(juju_model.istio_system) != 0 ? juju_model.istio_system[0].uuid : var.istio_system_model_uuid
}

resource "terraform_data" "deployed_at" {
  input = timestamp()

  lifecycle {
    ignore_changes = [input]
  }
}
