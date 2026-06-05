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

variable "s3_access_key" {
  description = "Access key for S3 storage."
  type        = string
  sensitive   = true
  default     = null
}

variable "s3_secret_key" {
  description = "Secret key for S3 storage."
  type        = string
  sensitive   = true
  default     = null
}

variable "tls_private_key" {
  type    = string
  default = null
}

variable "history_server_revision" {
  type        = string
  default     = null
  description = "Revision for the history server"
}

variable "integration_hub_revision" {
  type        = string
  default     = null
  description = "Revision for the integration hub"
}

variable "kyuubi_revision" {
  type        = string
  default     = null
  description = "Revision for Kyuubi"
}

variable "kyuubi_users_revision" {
  type        = string
  default     = null
  description = "Revision for Kyuubi users"
}

variable "metastore_revision" {
  type        = string
  default     = null
  description = "Revision for the metastore"
}

variable "zookeeper_revision" {
  type        = string
  default     = null
  description = "Revision for ZooKeeper"
}

variable "data_integrator_revision" {
  type        = string
  default     = null
  description = "Revision for the data integrator"
}

variable "s3_revision" {
  type        = string
  default     = null
  description = "Revision for S3"
}

variable "ssc_revision" {
  type        = string
  default     = null
  description = "Revision for SSC"
}

variable "azure_storage_revision" {
  type        = string
  default     = null
  description = "Revision for Azure storage"
}

variable "history_server_image" {
  type        = any
  default     = null
  description = "Image for the history server"
}

variable "integration_hub_image" {
  type        = any
  default     = null
  description = "Image for the integration hub"
}

variable "kyuubi_image" {
  type        = any
  default     = null
  description = "Image for Kyuubi"
}

variable "kyuubi_users_image" {
  type        = string
  default     = null
  description = "Image for Kyuubi users"
}

variable "metastore_image" {
  type        = string
  default     = null
  description = "Image for the metastore"
}

variable "zookeeper_image" {
  type        = string
  default     = null
  description = "Image for ZooKeeper"
}

variable "cos_configuration_revision" {
  type        = string
  default     = null
  description = "Revision for COS configuration"
}

variable "grafana_agent_revision" {
  type        = string
  default     = null
  description = "Revision for the Grafana agent"
}

variable "pushgateway_revision" {
  type        = string
  default     = null
  description = "Revision for the pushgateway"
}

variable "scrape_config_revision" {
  type        = string
  default     = null
  description = "Revision for the scrape configuration"
}

variable "grafana_agent_image" {
  type        = string
  default     = null
  description = "Image for the Grafana agent"
}

variable "pushgateway_image" {
  type        = string
  default     = null
  description = "Image for the pushgateway"
}

variable "spark_risk" {
  description = "Spark components risk channel"
  type        = string
  default     = "stable"

  validation {
    condition     = contains(["edge", "beta", "candidate", "stable"], var.spark_risk)
    error_message = "'spark_risk' can only take the following value: 'edge', 'beta', 'candidate' or 'stable'."
  }
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
  azure_storage_revision     = var.azure_storage_revision
  azure_storage_secret_key   = var.azure_storage_secret_key
  cos_configuration_revision = var.cos_configuration_revision
  data_integrator_revision   = var.data_integrator_revision
  grafana_agent_image        = var.grafana_agent_image
  grafana_agent_revision     = var.grafana_agent_revision
  history_server_image       = var.history_server_image
  history_server_revision    = var.history_server_revision
  integration_hub_image      = var.integration_hub_image
  integration_hub_revision   = var.integration_hub_revision
  kyuubi_config              = var.kyuubi_config
  kyuubi_image               = var.kyuubi_image
  kyuubi_revision            = var.kyuubi_revision
  kyuubi_users_image         = var.kyuubi_users_image
  kyuubi_users_revision      = var.kyuubi_users_revision
  kyuubi_users_size          = "500M"
  metastore_image            = var.metastore_image
  metastore_revision         = var.metastore_revision
  metastore_size             = "500M"
  pushgateway_image          = var.pushgateway_image
  pushgateway_revision       = var.pushgateway_revision
  s3_access_key              = var.s3_access_key
  s3_config                  = var.s3_config
  s3_revision                = var.s3_revision
  s3_secret_key              = var.s3_secret_key
  scrape_config_revision     = var.scrape_config_revision
  ssc_revision               = var.ssc_revision
  storage_backend            = var.storage_backend
  tls_private_key            = var.tls_private_key
  zookeeper_image            = var.zookeeper_image
  zookeeper_revision         = var.zookeeper_revision
  zookeeper_units            = 1
  spark_risk                 = var.spark_risk

  cos_offers = module.cos != [] ? {
    dashboard = module.cos[0].offers.grafana_dashboards.url
    logging   = module.cos[0].offers.loki_logging.url
    metrics   = module.cos[0].offers.prometheus_receive_remote_write.url
  } : null
}

output "models" {
  value = module.spark.models
}
