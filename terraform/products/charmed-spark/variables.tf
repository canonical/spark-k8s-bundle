# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "admin_password" {
  description = "The password for the Kyuubi admin user."
  type        = string
  sensitive   = true
  default     = null
}

variable "azure_storage_config" {
  description = "Azure Object storage information"
  type = object({
    container       = optional(string)
    credentials     = optional(string)
    path            = optional(string)
    protocol        = optional(string, "abfss")
    storage-account = optional(string)
  })
  default = {}
}

variable "azure_storage_revision" {
  description = "Charm revision for azure-storage-integrator"
  type        = number
  default     = null
  nullable    = true
}

variable "azure_storage_secret_key" {
  description = "Secret key to the Azure Storage account."
  type        = string
  sensitive   = true
  default     = null
}

variable "s3_access_key" {
  description = "AWS S3 Access key."
  type        = string
  sensitive   = true
  default     = null
}

variable "s3_secret_key" {
  description = "AWS S3 Secret key."
  type        = string
  sensitive   = true
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

variable "cos_configuration_revision" {
  description = "Charm revision for cos-configuration"
  type        = number
  default     = null
  nullable    = true
}

variable "cos_offers" {
  description = "Observability stack offers."
  type = object({
    dashboard = string
    logging   = string
    metrics   = string
  })
  default = null
}

variable "data_integrator_revision" {
  description = "Charm revision for data-integrator"
  type        = number
  default     = null
  nullable    = true
}

variable "otelcol_revision" {
  description = "Charm revision for opentelemetry-collector-k8s"
  type        = number
  default     = null
  nullable    = true
}

variable "history_server_config" {
  description = "History Server configuration options"
  type        = map(any)
  default     = {}
}

variable "history_server_image" {
  description = "Image for spark-history-server-k8s"
  type        = any
  default     = null
}

variable "history_server_revision" {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  default     = null
  nullable    = true
}

variable "integration_hub_image" {
  description = "Image for spark-integration-hub-k8s"
  type        = any
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
  nullable    = true
}

variable "kyuubi_config" {
  description = "Kyuubi configuration options."
  type        = map(any)
  default     = {}
}

variable "kyuubi_image" {
  description = "Image for kyuubi-k8s"
  type        = any
  default     = null
}

variable "kyuubi_revision" {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  default     = null
  nullable    = true
}

variable "kyuubi_units" {
  description = "Number of Kyuubi units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "logging_config" {
  description = "Logging configuration to be used"
  type        = string
  default     = "<root>=INFO"
}

variable "postgresql" {
  description = "PostgreSQL (16/stable) backing Kyuubi's auth database and the Hive metastore. `kind`: \"app\" (default, deploys one app for both), \"endpoint\" (existing in-model app, set `name`), or \"offer\" (cross-model offer, set `url`). `config` keys use 16/stable's hyphenated naming."
  type = object({
    kind     = optional(string, "app")
    name     = optional(string)
    url      = optional(string)
    config   = optional(map(any), {})
    revision = optional(number)
    image    = optional(any)
    size     = optional(string, "10G")
  })
  default = {}

  validation {
    condition     = contains(["app", "endpoint", "offer"], var.postgresql.kind)
    error_message = "'postgresql.kind' must be one of: 'app', 'endpoint', 'offer'."
  }

  validation {
    condition     = var.postgresql.kind != "endpoint" || (var.postgresql.name != null && var.postgresql.name != "")
    error_message = "'postgresql.name' must be set when 'postgresql.kind' is 'endpoint'."
  }

  validation {
    condition     = var.postgresql.kind != "offer" || (var.postgresql.url != null && var.postgresql.url != "")
    error_message = "'postgresql.url' must be set when 'postgresql.kind' is 'offer'."
  }
}

variable "pushgateway_image" {
  description = "Image for pushgateway"
  type        = any
  default     = null
}

variable "pushgateway_revision" {
  description = "Charm revision for pushgateway"
  type        = number
  default     = null
  nullable    = true
}

variable "scrape_config_revision" {
  description = "Charm revision for scrape_config"
  type        = number
  default     = null
  nullable    = true
}

variable "spark_model_name" {
  description = "The name of the juju model to deploy Spark to"
  type        = string
  default     = "spark"
}

variable "istio_system_model_name" {
  description = "Name of the Juju model to create for the managed Istio control plane."
  type        = string
  default     = "istio-system"
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

variable "model_uuid" {
  description = "Optional existing Juju model UUID to deploy Spark to. If provided, model creation is skipped in higher-level modules."
  type        = string
  default     = null
}

variable "istio_system_model_uuid" {
  description = "Existing Juju model UUID into which managed mode deploys istio-k8s. This does not reuse an existing Istio application and is ignored in external and disabled modes."
  type        = string
  default     = null

  validation {
    condition     = var.istio_system_model_uuid == null ? true : trimspace(var.istio_system_model_uuid) != ""
    error_message = "istio_system_model_uuid must be null or a non-empty Juju model UUID."
  }
}

variable "proxy" {
  description = "Proxy information for the deployment."
  type = object({
    http     = optional(string, "")
    https    = optional(string, "")
    no-proxy = optional(string, "")
  })
  default = {}
}

variable "ssc_revision" {
  description = "Charm revision for self-signed-certificates"
  type        = number
  default     = null
  nullable    = true
}

variable "s3_config" {
  description = "S3 integrator configuration"
  type = object({
    attributes                          = optional(string)
    bucket                              = optional(string)
    endpoint                            = optional(string)
    experimental-delete-older-than-days = optional(number)
    path                                = optional(string)
    region                              = optional(string)
    s3-api-version                      = optional(string)
    s3-uri-style                        = optional(string)
    storage-class                       = optional(string)
    tls-ca-chain                        = optional(string)
  })
  default = {}
}

variable "s3_revision" {
  description = "Charm revision for s3-integrator"
  type        = number
  default     = null
  nullable    = true
}

variable "storage_backend" {
  type        = string
  description = "Storage backend to be used"

  validation {
    condition     = contains(["azure_storage", "s3"], var.storage_backend)
    error_message = "Valid values for var: storage_backend are (s3, azure_storage)."
  }

  default = "s3"
}

variable "tls_private_key" {
  description = "The file path of the base64 encoded private key to use for TLS certificates."
  type        = string
  sensitive   = true
  default     = null
}

variable "zookeeper_image" {
  description = "Image for zookeeper-k8s"
  type        = any
  default     = null
}

variable "zookeeper_revision" {
  description = "Charm revision for zookeeper-k8s"
  type        = number
  default     = null
  nullable    = true
}

variable "zookeeper_units" {
  description = "Define the number of zookeeper units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "istio_ingress_k8s_revision" {
  description = "Revision of the istio-ingress-k8s application"
  type        = number
  default     = null
}

variable "istio_ingress_k8s_config" {
  description = "Configuration for istio-ingress-k8s application"
  type        = map(string)
  default     = {}
}

variable "istio_k8s_revision" {
  description = "Revision of the istio-k8s application"
  type        = number
  default     = null
  nullable    = true
}

variable "istio_k8s_config" {
  description = "Configuration for istio-k8s application"
  type        = map(string)
  default     = {}
}

variable "istio_beacon_k8s_revision" {
  description = "Revision of the istio-beacon-k8s application"
  type        = number
  default     = null
}

variable "istio_beacon_k8s_config" {
  description = "Configuration for istio-beacon-k8s application"
  type        = map(string)
  default     = {}
}

variable "service_mesh_mode" {
  description = "Service mesh ownership: disabled, managed (deploy istio-k8s), or external (use an existing compatible control plane on the Spark cluster)."
  type        = string
  default     = "disabled"
  nullable    = false

  validation {
    condition     = contains(["disabled", "managed", "external"], var.service_mesh_mode)
    error_message = "service_mesh_mode must be disabled, managed, or external."
  }
}

variable "istio_k8s_platform" {
  description = "Platform value for istio-k8s (always merged into its config as 'platform', including an empty string)."
  type        = string
  default     = ""
}

variable "traefik_revision" {
  description = "Revision of the traefik-k8s application (used as history server ingress when the service mesh is disabled)."
  type        = number
  default     = null
}

variable "traefik_config" {
  description = "Configuration for the traefik-k8s application."
  type        = map(string)
  default     = {}
}