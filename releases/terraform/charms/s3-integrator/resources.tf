# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

locals {
  target_model_uuid = var.model_uuid != null ? var.model_uuid : data.juju_model.spark.id
}

data "juju_model" "spark" {
  name = var.model
}
