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

variable "s3_config" {
  type = map(any)
}

variable "tls_private_key" {
  type    = string
  default = null
}

variable "zookeeper_units" {
  type = number
}
variable "kyuubi_users_size" {
  type = string
}
variable "metastore_size" {
  type = string
}
variable "zookeeper_size" {
  type = string
}

resource "juju_model" "spark" {
  count = (var.model_uuid == null && var.create_model == true) ? 1 : 0

  name       = var.spark_model_name
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "spark" {
  depends_on = [juju_model.spark]
  source     = "./products/charmed-spark-3.4"

  model_uuid   = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid
  create_model = false

  admin_password    = var.admin_password
  kyuubi_config     = var.kyuubi_config
  kyuubi_users_size = var.kyuubi_users_size
  metastore_size    = var.metastore_size
  s3_config         = var.s3_config
  storage_backend   = var.storage_backend
  tls_private_key   = var.tls_private_key
  zookeeper_size    = var.zookeeper_size
  zookeeper_units   = var.zookeeper_units
}
