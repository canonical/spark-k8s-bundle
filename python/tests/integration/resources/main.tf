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

variable "K8S_CLOUD" {
  type    = string
  default = "microk8s"
}

variable "K8S_CREDENTIAL" {
  type    = string
  default = "microk8s"
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

module "cos" {
  count = var.cos_model_uuid == null ? 0 : 1
  # TODO: Pin to tag once available
  source       = "git::https://github.com/canonical/observability-stack//terraform/cos-lite?ref=cd55b1d"
  model_uuid   = var.cos_model_uuid
  internal_tls = false
  alertmanager = { revision = 191 }
  catalogue    = { revision = 113 }
  grafana      = { revision = 180 }
  loki         = { revision = 217 }
  prometheus   = { revision = 287 }
  traefik      = { revision = 281 }


}

resource "juju_model" "spark" {
  count      = (var.model_uuid == null && var.create_model == true) ? 1 : 0
  name       = var.spark_model_name
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "spark" {
  depends_on = [juju_model.spark, module.cos]
  source     = "./products/charmed-spark-<spark_flavor>" # filled by test fixture

  model_uuid   = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid
  create_model = false

  admin_password           = var.admin_password
  azure_storage_config     = var.azure_storage_config
  azure_storage_secret_key = var.azure_storage_secret_key
  kyuubi_config            = var.kyuubi_config
  kyuubi_users_size        = "500M"
  metastore_size           = "500M"
  s3_config                = var.s3_config
  storage_backend          = var.storage_backend
  tls_private_key          = var.tls_private_key
  zookeeper_size           = "10G"
  zookeeper_units          = 1

  cos_offers = module.cos != [] ? {
    dashboard = module.cos[0].offers.grafana_dashboards.url
    logging   = module.cos[0].offers.loki_logging.url
    metrics   = module.cos[0].offers.prometheus_receive_remote_write.url
  } : null
}

output "models" {
  value = module.spark.models
}
