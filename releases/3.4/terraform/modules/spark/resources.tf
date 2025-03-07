# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

data "juju_model" "spark" {
  name = var.model
}

locals {
  certificates = "certificates"
}

module "ssc" {
  count       = var.use_manual_tls ? 0 : 1
  source      = "git::https://github.com/canonical/self-signed-certificates-operator//terraform"
  model       = data.juju_model.spark.name
  channel     = "latest/edge"
  app_name    = local.certificates
  revision    = 163
  constraints = "arch=amd64"
  base        = "ubuntu@22.04"
  units       = 1
}

# TODO (tls): Figure out how to pass the certs in this case
module "manualtls" {
  count    = var.use_manual_tls ? 1 : 0
  source   = "../tls"
  model    = data.juju_model.spark.name
  channel  = "latest/stable"
  app_name = local.certificates
}
