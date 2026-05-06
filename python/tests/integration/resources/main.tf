# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=1.0.0"
    }
  }
}

variable "create_model" {
  description = "Should terraform create the Juju models? If set to false, assume the models are created by a different mechanism."
  type        = bool
  default     = true
  nullable    = false
}

variable "cos_model_uuid" {
  type    = string
  default = null
}

variable "spark_model_name" {
  type    = string
  default = "spark-test-model"
}

variable "model_uuid" {
  type    = string
  default = null
}
variable "storage_backend" {
  type = string
}

variable "admin_password" {
  type = string
}

variable "kyuubi_config" {
  type = map(any)
}

variable "azure_storage_config" {
  type    = map(any)
  default = {}
}

variable "azure_storage_secret_key" {
  description = "Secret key to the Azure Storage account."
  type        = string
  sensitive   = true
  default     = null
}

variable "s3_config" {
  type    = map(any)
  default = {}
}

variable "tls_private_key" {
  type    = string
  default = null
}

variable "charmed_spark" {
  type = object({
    history_server_revision  = optional(string)
    integration_hub_revision = optional(string)
    kyuubi_revision          = optional(string)
    kyuubi_users_revision    = optional(string)
    metastore_revision       = optional(string)
    zookeeper_revision       = optional(string)
    data_integrator_revision = optional(string)
    s3_revision              = optional(string)
    ssc_revision             = optional(string)
    azure_storage_revision   = optional(string)
    history_server_image     = optional(string)
    integration_hub_image    = optional(string)
    kyuubi_image             = optional(string)
    kyuubi_users_image       = optional(string)
    metastore_image          = optional(string)
    zookeeper_image          = optional(string)
  })
  default = {}
}

variable "observability" {
  type = object({
    cos_configuration_revision = optional(string)
    grafana_agent_revision     = optional(string)
    pushgateway_revision       = optional(string)
    scrape_config_revision     = optional(string)
    grafana_agent_image        = optional(string)
    pushgateway_image          = optional(string)
  })
  default = {}
}

module "cos" {
  count = var.cos_model_uuid == null ? 0 : 1
  # TODO: Pin to tag once available
  # branch: track/2
  source       = "git::https://github.com/canonical/observability-stack//terraform/cos-lite?ref=04ab6c618dbbec62292a052a61cdb402d80e5974"
  model_uuid   = var.cos_model_uuid
  internal_tls = false
}

resource "juju_model" "spark" {
  count = (var.model_uuid == null && var.create_model == true) ? 1 : 0
  name  = var.spark_model_name
}

module "spark" {
  depends_on = [juju_model.spark, module.cos]
  source     = "./products/charmed-spark-<spark_flavor>" # filled by test fixture

  model_uuid   = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid
  create_model = false

  admin_password             = var.admin_password
  azure_storage_config       = var.azure_storage_config
  azure_storage_revision     = var.charmed_spark.azure_storage_revision
  azure_storage_secret_key   = var.azure_storage_secret_key
  cos_configuration_revision = var.observability.cos_configuration_revision
  data_integrator_revision   = var.charmed_spark.data_integrator_revision
  grafana_agent_image        = var.observability.grafana_agent_image
  grafana_agent_revision     = var.observability.grafana_agent_revision
  history_server_image       = var.charmed_spark.history_server_image
  history_server_revision    = var.charmed_spark.history_server_revision
  integration_hub_image      = var.charmed_spark.integration_hub_image
  integration_hub_revision   = var.charmed_spark.integration_hub_revision
  kyuubi_config              = var.kyuubi_config
  kyuubi_image               = var.charmed_spark.kyuubi_image
  kyuubi_revision            = var.charmed_spark.kyuubi_revision
  kyuubi_users_image         = var.charmed_spark.kyuubi_users_image
  kyuubi_users_revision      = var.charmed_spark.kyuubi_users_revision
  kyuubi_users_size          = "500M"
  metastore_image            = var.charmed_spark.metastore_image
  metastore_revision         = var.charmed_spark.metastore_revision
  metastore_size             = "500M"
  pushgateway_image          = var.observability.pushgateway_image
  pushgateway_revision       = var.observability.pushgateway_revision
  s3_config                  = var.s3_config
  s3_revision                = var.charmed_spark.s3_revision
  scrape_config_revision     = var.observability.scrape_config_revision
  ssc_revision               = var.charmed_spark.ssc_revision
  storage_backend            = var.storage_backend
  tls_private_key            = var.tls_private_key
  zookeeper_image            = var.charmed_spark.zookeeper_image
  zookeeper_revision         = var.charmed_spark.zookeeper_revision
  zookeeper_units            = 1

  cos_offers = module.cos != [] ? {
    dashboard = module.cos[0].offers.grafana_dashboards.url
    logging   = module.cos[0].offers.loki_logging.url
    metrics   = module.cos[0].offers.prometheus_receive_remote_write.url
  } : null
}

output "models" {
  value = module.spark.models
}
