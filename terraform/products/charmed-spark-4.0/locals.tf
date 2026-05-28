# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  model_uuid = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid
}

resource "terraform_data" "deployed_at" {
  input = timestamp()

  lifecycle {
    ignore_changes = [input]
  }
}
