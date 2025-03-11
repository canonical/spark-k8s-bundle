# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=0.16.0"
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

module "ssc" {
  depends_on  = [juju_model.spark]
  source      = "git::https://github.com/canonical/self-signed-certificates-operator//terraform"
  model       = var.model
  channel     = "latest/edge"
  revision    = 163
  constraints = "arch=amd64"
  base        = "ubuntu@22.04"
  units       = 1
}

module "spark" {
  depends_on                = [juju_model.spark, module.ssc]
  source                    = "./modules/spark"
  model                     = var.model
  kyuubi_user               = var.kyuubi_user
  zookeeper_units           = var.zookeeper_units
  tls_app_name              = module.ssc.app_name
  tls_certificates_endpoint = module.ssc.provides.certificates
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
  source     = "./external/cos"
  model      = var.cos_model
}

module "observability" {
  depends_on       = [module.spark, module.cos]
  count            = var.cos_model == null ? 0 : 1
  source           = "./modules/observability"
  dashboards_offer = one(module.cos[*].dashboards_offer)
  metrics_offer    = one(module.cos[*].metrics_offer)
  logging_offer    = one(module.cos[*].logging_offer)
  spark_model      = var.model
  spark_charms     = module.spark.charms
}
