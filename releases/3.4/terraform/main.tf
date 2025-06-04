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

  spark_history_server_revision = var.spark_history_server_revision != null ? var.spark_history_server_revision : local.revisions.spark_history_server
  spark_history_server_image = var.spark_history_server_image != null ? var.spark_history_server_image : local.images.spark_history_server
  spark_integration_hub_revision = var.spark_integration_hub_revision != null ? var.spark_integration_hub_revision : local.revisions.spark_integration_hub
  spark_integration_hub_image = var.spark_integration_hub_image != null ? var.spark_integration_hub_image : local.images.spark_integration_hub
  kyuubi_revision = var.kyuubi_revision != null ? var.kyuubi_revision : local.revisions.kyuubi
  kyuubi_image = var.kyuubi_image != null ? var.kyuubi_image : local.images.kyuubi
  kyuubi_users_revision = var.kyuubi_users_revision != null ? var.kyuubi_users_revision : local.revisions.kyuubi_users
  kyuubi_users_image = var.kyuubi_users_image != null ? var.kyuubi_users_image : local.images.kyuubi_users
  metastore_revision = var.metastore_revision != null ? var.metastore_revision : local.revisions.metastore
  metastore_image = var.metastore_image != null ? var.metastore_image : local.images.metastore
  zookeeper_revision = var.zookeeper_revision != null ? var.zookeeper_revision : local.revisions.zookeeper
  zookeeper_image = var.zookeeper_image != null ? var.zookeeper_image : local.images.zookeeper
}

module "azure" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "azure" ? 1 : 0
  source       = "./modules/azure-storage"
  model        = var.model
  spark_charms = module.spark.charms
  azure        = var.azure

  azure_storage_integrator_revision = var.azure_storage_integrator_revision != null ? var.azure_storage_integrator_revision : local.revisions.azure_storage_integrator
}

module "s3" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "s3" ? 1 : 0
  source       = "./modules/s3"
  model        = var.model
  spark_charms = module.spark.charms
  s3           = var.s3

  s3_integrator_revision = var.s3_integrator_revision != null ? var.s3_integrator_revision : local.revisions.s3_integrator
}

module "external_cos" {
  depends_on   = [juju_model.cos]
  count        = var.cos.deployed == "bundled" ? 1 : 0
  source       = "./external/cos"
  model        = var.cos.model
  cos_tls_ca   = var.cos.tls.ca
  cos_tls_cert = var.cos.tls.cert
  cos_tls_key  = var.cos.tls.key
}


module "observability" {
  depends_on       = [module.spark, module.external_cos]
  count            = var.cos.deployed == "no" ? 0 : 1
  source           = "./modules/observability"
  dashboards_offer = var.cos.deployed == "external" ? var.cos.offers.dashboard : one(module.external_cos[*].dashboards_offer)
  logging_offer    = var.cos.deployed == "external" ? var.cos.offers.logging : one(module.external_cos[*].logging_offer)
  metrics_offer    = var.cos.deployed == "external" ? var.cos.offers.metrics : one(module.external_cos[*].metrics_offer)
  spark_model      = var.model
  spark_charms     = module.spark.charms

  grafana_agent_revision = var.grafana_agent_revision != null ? var.grafana_agent_revision : local.revisions.grafana_agent
  # grafana_agent_image = var.grafana_agent_image != null ? var.grafana_agent_image : local.images.grafana_agent
  cos_configuration_revision = var.cos_configuration_revision != null ? var.cos_configuration_revision : local.revisions.cos_configuration
  prometheus_pushgateway_revision = var.prometheus_pushgateway_revision != null ? var.prometheus_pushgateway_revision : local.revisions.prometheus_pushgateway
  # prometheus_pushgateway_image = var.prometheus_pushgateway_image != null ? var.prometheus_pushgateway_image : local.images.prometheus_pushgateway
  prometheus_scrape_config_revision = var.prometheus_scrape_config_revision != null ? var.prometheus_scrape_config_revision : local.revisions.prometheus_scrape_config
}
