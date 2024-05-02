# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# ====================
# PATTERN TO BE TESTED
# ====================
# resource "juju_model" "spark" {
#   lifecycle {
#     replace_triggered_by = []
#   }
#
#   name = var.model
#
#   cloud {
#     name = "microk8s"
#   }
#
#   config = {
#     logging-config              = "<root>=DEBUG"
#     update-status-hook-interval = "5m"
#   }
# }

data "juju_model" "spark" {
  name = var.model
}

module "base" {
  source = "./base"

  model = data.juju_model.spark.name
  s3 = var.s3
  kyuubi_user = var.kyuubi_user
}

module "cos" {
  count  = var.cos_model == null ? 0 : 1
  source = "./cos"

  model = data.juju_model.spark.name
  integration_hub = module.base.charms.hub
  cos_model = var.cos_model
}