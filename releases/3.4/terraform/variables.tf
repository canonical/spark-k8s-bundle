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
    model    = optional(string, "cos")
    deployed = optional(string, "bundled")
    offers = optional(object({
      dashboard = optional(string, null),
      metrics   = optional(string, null),
      logging   = optional(string, null)
    }), {}),
    tls = optional(object({
      cert = optional(string, "")
      key  = optional(string, "")
      ca   = optional(string, "")
    }), {})
  })
  default = { model = "cos", deployed = "bundled", offers = {}, tls = {} }

  validation {
    condition     = contains(["external", "bundled", "no"], var.cos.deployed)
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
    condition     = contains(["azure_storage", "s3"], var.storage_backend)
    error_message = "Valid values for var: test_variable are (s3, azure_storage)."
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

variable "azure_storage" {
  description = "Azure Object storage information"
  type = object({
    container       = optional(string, "azurecontainer")
    storage_account = optional(string, "azurestorageaccount")
    secret_key      = optional(string, "azurestoragesecret")
    protocol        = optional(string, "abfss")
  })
  default = {}
}

variable "admin_password" {
  description = "The password for the admin user."
  type        = string
  sensitive   = true
  default     = null
}

variable "tls_private_key" {
  description = "The private key to be used for TLS certificates."
  type        = string
  sensitive   = true
  default     = null
}

variable "kyuubi_profile" {
  description = "The profile to be used for Kyuubi; should be one of 'testing', 'staging' and 'production'."
  type        = string
  nullable    = false
  default     = "production"
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

variable "history_server_revision" {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  default     = null
}

variable "history_server_image" {
  description = "Image for spark-history-server-k8s"
  type        = map(string)
  default     = null
}

variable "integration_hub_revision" {
  description = "Charm revision for spark-integration-hub-k8s"
  type        = number
  default     = null
}

variable "integration_hub_image" {
  description = "Image for spark-integration-hub-k8s"
  type        = map(string)
  default     = null
}

variable "kyuubi_revision" {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  default     = null
}

variable "kyuubi_image" {
  description = "Image for kyuubi-k8s"
  type        = map(string)
  default     = null
}

variable "kyuubi_users_revision" {
  description = "Charm revision for postgresql-k8s (auth-db)"
  type        = number
  default     = null
}

variable "kyuubi_users_image" {
  description = "Image for postgresql-k8s (auth-db)"
  type        = map(string)
  default     = null
}

variable "kyuubi_k8s_node_selectors" {
  description = "Worker pool specification for Kyuubi"
  type        = string
  default     = ""
}

variable "metastore_revision" {
  description = "Charm revision for postgresql-k8s (metastore)"
  type        = number
  default     = null
}

variable "metastore_image" {
  description = "Image for postgresql-k8s (metastore)"
  type        = map(string)
  default     = null
}

variable "zookeeper_revision" {
  description = "Charm revision for zookeeper-k8s"
  type        = number
  default     = null
}

variable "zookeeper_image" {
  description = "Image for zookeeper-k8s"
  type        = map(string)
  default     = null
}

variable "data_integrator_revision" {
  description = "Charm revision for data-integrator"
  type        = number
  default     = null
}

variable "s3_revision" {
  description = "Charm revision for s3-integrator"
  type        = number
  default     = null
}

variable "azure_storage_revision" {
  description = "Charm revision for azure-storage-integrator"
  type        = number
  default     = null
}

variable "grafana_agent_revision" {
  description = "Charm revision for grafana-agent-k8s"
  type        = number
  default     = null
}

variable "cos_configuration_revision" {
  description = "Charm revision for cos-configuration-k8s"
  type        = number
  default     = null
}

variable "pushgateway_revision" {
  description = "Charm revision for prometheus-pushgateway-k8s"
  type        = number
  default     = null
}

variable "scrape_config_revision" {
  description = "Charm revision for prometheus-scrape-config-k8s"
  type        = number
  default     = null
}

variable "certificate_common_name" {
  description = "Common name for the certificate to be used in self-signed"
  type        = string
  default     = null
}

