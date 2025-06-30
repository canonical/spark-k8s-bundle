# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_model" "spark" {
  count      = var.create_model == true ? 1 : 0
  name       = var.model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

resource "juju_model" "cos" {
  count      = var.cos.deployed == "bundled" && var.create_model == true ? 1 : 0
  name       = var.cos.model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "ssc" {
  depends_on  = [juju_model.spark]
  source      = "git::https://github.com/canonical/self-signed-certificates-operator//terraform"
  model       = var.model
  app_name    = "certificates"
  channel     = "latest/stable"
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
  admin_password            = var.admin_password
  zookeeper_units           = var.zookeeper_units
  tls_app_name              = module.ssc.app_name
  tls_certificates_endpoint = module.ssc.provides.certificates

  history_server_revision  = var.history_server_revision != null ? var.history_server_revision : local.revisions.history_server
  history_server_image     = var.history_server_image != null ? var.history_server_image : local.images.history_server
  integration_hub_revision = var.integration_hub_revision != null ? var.integration_hub_revision : local.revisions.integration_hub
  integration_hub_image    = var.integration_hub_image != null ? var.integration_hub_image : local.images.integration_hub
  kyuubi_revision          = var.kyuubi_revision != null ? var.kyuubi_revision : local.revisions.kyuubi
  kyuubi_image             = var.kyuubi_image != null ? var.kyuubi_image : local.images.kyuubi
  kyuubi_users_revision    = var.kyuubi_users_revision != null ? var.kyuubi_users_revision : local.revisions.kyuubi_users
  kyuubi_users_image       = var.kyuubi_users_image != null ? var.kyuubi_users_image : local.images.kyuubi_users
  metastore_revision       = var.metastore_revision != null ? var.metastore_revision : local.revisions.metastore
  metastore_image          = var.metastore_image != null ? var.metastore_image : local.images.metastore
  zookeeper_revision       = var.zookeeper_revision != null ? var.zookeeper_revision : local.revisions.zookeeper
  zookeeper_image          = var.zookeeper_image != null ? var.zookeeper_image : local.images.zookeeper
  data_integrator_revision = var.data_integrator_revision != null ? var.data_integrator_revision : local.revisions.data_integrator
}

module "azure_storage" {
  depends_on    = [module.spark]
  count         = var.storage_backend == "azure_storage" ? 1 : 0
  source        = "./modules/azure-storage"
  model         = var.model
  spark_charms  = module.spark.charms
  azure_storage = var.azure_storage

  azure_storage_revision = var.azure_storage_revision != null ? var.azure_storage_revision : local.revisions.azure_storage
}

module "s3" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "s3" ? 1 : 0
  source       = "./modules/s3"
  model        = var.model
  spark_charms = module.spark.charms
  s3           = var.s3

  s3_revision = var.s3_revision != null ? var.s3_revision : local.revisions.s3
}

module "bundled_cos" {
  depends_on   = [juju_model.cos]
  count        = var.cos.deployed == "bundled" ? 1 : 0
  source       = "./external/cos"
  model        = var.cos.model
  cos_tls_ca   = var.cos.tls.ca
  cos_tls_cert = var.cos.tls.cert
  cos_tls_key  = var.cos.tls.key
}


module "observability" {
  depends_on       = [module.spark, module.bundled_cos]
  count            = var.cos.deployed == "no" ? 0 : 1
  source           = "./modules/observability"
  dashboards_offer = var.cos.deployed == "external" ? var.cos.offers.dashboard : one(module.bundled_cos[*].dashboards_offer)
  logging_offer    = var.cos.deployed == "external" ? var.cos.offers.logging : one(module.bundled_cos[*].logging_offer)
  metrics_offer    = var.cos.deployed == "external" ? var.cos.offers.metrics : one(module.bundled_cos[*].metrics_offer)
  spark_model      = var.model
  spark_charms     = module.spark.charms

  grafana_agent_revision     = var.grafana_agent_revision != null ? var.grafana_agent_revision : local.revisions.grafana_agent
  cos_configuration_revision = var.cos_configuration_revision != null ? var.cos_configuration_revision : local.revisions.cos_configuration
  pushgateway_revision       = var.pushgateway_revision != null ? var.pushgateway_revision : local.revisions.pushgateway
  scrape_config_revision     = var.scrape_config_revision != null ? var.scrape_config_revision : local.revisions.scrape_config
}
