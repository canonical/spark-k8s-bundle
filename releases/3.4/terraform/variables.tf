# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Juju

variable "K8S_CLOUD" {
  type        = string
  description = "The kubernetes juju cloud name."
  default     = "microk8s"
}

variable "K8S_CREDENTIAL" {
  type        = string
  description = "The name of the kubernetes juju credential."
  default     = "microk8s"
}

# Models

variable "model" {
  description = "The name of the juju model to deploy Spark to"
  type        = string
  default     = "spark"
}

variable "create_model" {
  description = "Should terraform create the Juju models? If set to false, assume the models are created by a different mechanism."
  type        = bool
  default     = true
  nullable    = false
}

# cos specifics

variable "cos" {
  description = "Observability settings"
  type = object({
    model           = optional(string, "cos")
    deployed        = optional(string, "bundled")
    offers          = optional(object({
        dashboard  = optional(string, null),
        metrics    = optional(string, null),
        logging    = optional(string, null)
    }), {}),
    tls = optional(object({
        cert = optional(string, "")
        key  = optional(string, "")
        ca   = optional(string, "")
    }), {})
  })
  default = {model="cos", deployed="bundled", offers={}, tls={}}

  validation {
    condition = contains(["external", "bundled", "no"], var.cos.deployed)
    error_message = "Valid values for var: cos.deployed are (external, bundled, no)"
  }

  validation {
    condition = var.cos.deployed != "external" || alltrue([
      var.cos.offers.dashboard != null,
      var.cos.offers.metrics != null,
      var.cos.offers.logging != null,
    ])
    error_message = "When using external cos, please define all offers variables"
  }

}

# Storage

variable "storage_backend" {
  type        = string
  description = "Storage backend to be used"

  validation {
    condition     = contains(["azure", "s3"], var.storage_backend)
    error_message = "Valid values for var: test_variable are (s3, azure)."
  }

  default = "s3"
}

variable "s3" {
  description = "S3 Bucket information"
  type = object({
    bucket   = optional(string, "spark-test")
    endpoint = optional(string, "https://s3.amazonaws.com")
  })
  default = {}
}

variable "azure" {
  description = "Azure Object storage information"
  type = object({
    container       = optional(string, "azurecontainer")
    storage_account = optional(string, "azurestorageaccount")
    secret_key      = optional(string, "azurestoragesecret")
    protocol        = optional(string, "abfss")
  })
  default = {}
}

variable "kyuubi_user" {
  description = "Define the user to be used for running Kyuubi enginers"
  type        = string
  default     = "kyuubi-spark-engine"
}

variable "zookeeper_units" {
  description = "Define the number of zookeeper units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}
