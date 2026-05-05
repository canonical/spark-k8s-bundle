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

variable "history_server_revision" {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  default     = null
}

variable "kyuubi_revision" {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  default     = null
}

variable "integration_hub_revision" {
  description = "Charm revision for spark-integration-hub-k8s"
  type        = number
  default     = null
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
  azure_storage_secret_key   = var.azure_storage_secret_key
  cos_configuration_revision = var.observability.cos_configuration_revision
  grafana_agent_image        = var.observability.grafana_agent_image
  grafana_agent_revision     = var.observability.grafana_agent_revision
  history_server_revision    = var.history_server_revision
  integration_hub_revision   = var.integration_hub_revision
  kyuubi_config              = var.kyuubi_config
  kyuubi_revision            = var.kyuubi_revision
  kyuubi_users_size          = "500M"
  metastore_size             = "500M"
  pushgateway_image          = var.observability.pushgateway_image
  pushgateway_revision       = var.observability.pushgateway_revision
  s3_config                  = var.s3_config
  scrape_config_revision     = var.observability.scrape_config_revision
  storage_backend            = var.storage_backend
  tls_private_key            = var.tls_private_key
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
