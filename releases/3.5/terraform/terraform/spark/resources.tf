# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

resource "juju_model" "spark" {
  name       = var.model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}
