# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      source  = "juju/juju"
      version = "0.16.0"
    }
  }
}

provider "juju" {}


resource "juju_model" "spark" {
  count      = var.create_model == true ? 1 : 0
  name       = var.model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

resource "juju_model" "cos" {
  count      = (var.create_model == true && var.cos_model != null) ? 1 : 0
  name       = var.cos_model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "spark" {
  depends_on      = [juju_model.spark]
  source          = "./modules/spark"
  model           = var.model
  kyuubi_user     = var.kyuubi_user
  zookeeper_units = var.zookeeper_units
}


module "azure" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "azure" ? 1 : 0
  source       = "./modules/azure-storage"
  model        = var.model
  spark_charms = module.spark.charms
  azure        = var.azure
}

module "s3" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "s3" ? 1 : 0
  source       = "./modules/s3"
  model        = var.model
  spark_charms = module.spark.charms
  s3           = var.s3
}

module "cos" {
  depends_on = [juju_model.cos]
  count      = var.cos_model == null ? 0 : 1
  source     = "./modules/cos"
  model      = var.cos_model
}

module "observability" {
  depends_on   = [module.spark, module.cos]
  count        = var.cos_model == null ? 0 : 1
  source       = "./modules/observability"
  cos_model    = var.cos_model
  cos_user     = one(module.cos[*].user)
  cos_charms   = one(module.cos[*].charms)
  spark_model  = var.model
  spark_charms = module.spark.charms
}
