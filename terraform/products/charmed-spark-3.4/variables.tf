# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "admin_password" {
  description = "The password for the admin user."
  type        = string
  sensitive   = true
  default     = null
}


variable "azure_storage_config" {
  description = "Azure Object storage information"
  type = object({
    container       = optional(string, "azurecontainer")
    storage_account = optional(string, "azurestorageaccount")
    secret_key      = optional(string, "azurestoragesecret")
    protocol        = optional(string, "abfss")
  })
  default = {}
}

variable "azure_storage_revision" {
  description = "Charm revision for azure-storage-integrator"
  type        = number
  default     = null
}

variable "certificate_common_name" {
  description = "Common name for the certificate to be used in self-signed"
  type        = string
  default     = "charmed-spark"
}

variable "create_model" {
  description = "Should terraform create the Juju models? If set to false, assume the models are created by a different mechanism."
  type        = bool
  default     = true
  nullable    = false
}

variable "data_integrator_revision" {
  description = "Charm revision for data-integrator"
  type        = number
  default     = null
}

variable "grafana_agent_revision" {
  description = "Charm revision for grafana-agent-k8s"
  type        = number
  default     = null
}

variable "history_server_config" {
  description = "History Server configuration options"
  type        = map(any)
  default     = {}
}

variable "history_server_image" {
  description = "Image for spark-history-server-k8s"
  type        = string
  default     = null
}

variable "history_server_revision" {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  default     = null
}

variable "integration_hub_image" {
  description = "Image for spark-integration-hub-k8s"
  type        = string
  default     = null
}

variable "integration_hub_config" {
  description = "Integration Hub configuration options."
  type        = map(any)
  default     = {}
}

variable "integration_hub_revision" {
  description = "Charm revision for spark-integration-hub-k8s"
  type        = number
  default     = null
}

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

variable "juju_controller" {
  description = "Controller information: endpoint, username, password and CA certificate."
  type = object({
    endpoint = string
    username = string
    password = string
    ca       = string
  })
  default = null
}

variable "kyuubi_config" {
  description = "Kyuubi configuration options."
  type        = map(any)
  default     = {}
}

variable "kyuubi_image" {
  description = "Image for kyuubi-k8s"
  type        = string
  default     = null
}

variable "kyuubi_revision" {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  default     = null
}

variable "kyuubi_units" {
  description = "Number of Kyuubi units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "kyuubi_users_image" {
  description = "Image for postgresql-k8s (auth-db)"
  type        = string
  default     = null
}

variable "kyuubi_users_revision" {
  description = "Charm revision for postgresql-k8s (auth-db)"
  type        = number
  default     = null
}

variable "kyuubi_users_size" {
  description = "Storage size for the Kyuubi users database"
  type        = string
  default     = "1G"
}

variable "metastore_image" {
  description = "Image for postgresql-k8s (metastore)"
  type        = string
  default     = null
}

variable "metastore_revision" {
  description = "Charm revision for postgresql-k8s (metastore)"
  type        = number
  default     = null
}

variable "metastore_size" {
  description = "Storage size for the metastore database"
  type        = string
  default     = "10G"
}

variable "spark_model_name" {
  description = "The name of the juju model to deploy Spark to"
  type        = string
  default     = "spark-test"
}

variable "model_uuid" {
  description = "Optional existing Juju model UUID to deploy Spark to. If provided, model creation is skipped in higher-level modules."
  type        = string
  default     = null
}

variable "proxy" {
  description = "Proxy information for the deployment."
  type = object({
    http     = optional(string, "")
    https    = optional(string, "")
    no_proxy = optional(string, "")
  })
  default = {}
}

variable "s3_config" {
  description = "S3 Bucket information"
  type = object({
    bucket   = optional(string, "spark-test")
    endpoint = optional(string, "https://s3.amazonaws.com")
    region   = optional(string, "us-east-1")
  })
  default = {}
}

variable "s3_revision" {
  description = "Charm revision for s3-integrator"
  type        = number
  default     = null
}

variable "storage_backend" {
  type        = string
  description = "Storage backend to be used"

  validation {
    condition     = contains(["azure_storage", "s3"], var.storage_backend)
    error_message = "Valid values for var: test_variable are (s3, azure_storage)."
  }

  default = "s3"
}

variable "tls_private_key" {
  description = "The file path of the private key to use for TLS certificates."
  type        = string
  sensitive   = true
  default     = null
}

variable "zookeeper_image" {
  description = "Image for zookeeper-k8s"
  type        = map(string)
  default     = null
}

variable "zookeeper_revision" {
  description = "Charm revision for zookeeper-k8s"
  type        = number
  default     = null
}

variable "zookeeper_size" {
  description = "Storage size for the metastore database"
  type        = string
  default     = "10G"
}

variable "zookeeper_units" {
  description = "Define the number of zookeeper units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}
