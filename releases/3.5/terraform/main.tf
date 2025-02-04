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

module "spark" {
  source = "./terraform/spark"

  model          = var.model
  K8S_CLOUD      = var.K8S_CLOUD
  K8S_CREDENTIAL = var.K8S_CREDENTIAL
  kyuubi_user    = var.kyuubi_user
}


module "azure" {
  depends_on = [module.spark]
  count      = var.storage_backend == "azure" ? 1 : 0

  source = "./terraform/azure-storage"

  model        = var.model
  spark_charms = module.spark.charms
  azure        = var.azure
}

module "s3" {
  depends_on = [module.spark]
  count      = var.storage_backend == "s3" ? 1 : 0

  source = "./terraform/s3"

  model        = var.model
  spark_charms = module.spark.charms
  s3           = var.s3
}

module "cos" {
  depends_on = [module.spark, module.s3, module.azure]
  count      = var.cos_model == null ? 0 : 1

  source = "./terraform/cos"

  model          = var.cos_model
  K8S_CLOUD      = var.K8S_CLOUD
  K8S_CREDENTIAL = var.K8S_CREDENTIAL
}

module "observability" {
  depends_on = [module.spark, module.cos]
  count      = var.cos_model == null ? 0 : 1

  source = "./terraform/observability"

  cos_model    = var.cos_model
  cos_user     = one(module.cos[*].user)
  cos_charms   = one(module.cos[*].charms)
  spark_model  = var.model
  spark_charms = module.spark.charms
}
