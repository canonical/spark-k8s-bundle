# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "certificates" {
  name  = var.app_name
  model = data.juju_model.spark.name

  charm {
    name    = "manual-tls-certificates"
    channel = var.channel
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}
