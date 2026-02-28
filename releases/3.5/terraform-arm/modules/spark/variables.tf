# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define spark-specific variables

variable "model" {
  description = "Name of the Juju Model to deploy to."
  type        = string
  nullable    = false
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
  description = "User name to be used for running Kyuubi engines."
  type        = string
  nullable    = false
  default     = "kyuubi-spark-engine"
}

variable "enable_dynamic_allocation" {
  description = "Enable dynamic allocation of pods for Spark jobs."
  type        = bool
  default     = false
}

variable "kyuubi_k8s_node_selectors" {
  description = "Comma separated label:value selectors for K8s pods in Kyuubi."
  type        = string
  default     = null
}

variable "kyuubi_loadbalancer_extra_annotations" {
  description = "Optional extra annotations to be supplied to the load balancer service in Kyuubi."
  type        = string
  default     = null
}

variable "kyuubi_gpu_enable" {
  description = "Enable GPU acceleration for SparkSQLEngine."
  type        = bool
  nullable    = false
}

variable "kyuubi_gpu_engine_executors_limit" {
  description = "Limit the number of GPUs an engine can schedule executor pods on."
  type        = number
  nullable    = false
}

variable "kyuubi_gpu_pinned_memory" {
  description = "Set the host memory (in GB) per executor reserved for fast data transfer on GPUs."
  type        = number
  nullable    = false
}

variable "kyuubi_driver_pod_template" {
  description = "Define K8s driver pod from a file accessible in the object storage."
  type        = string
  default     = null
}

variable "kyuubi_executor_pod_template" {
  description = "Define K8s executor pod from a file accessible in the object storage."
  type        = string
  default     = null
}

variable "kyuubi_executor_cores" {
  description = "Set kyuubi executor pods cpu cores."
  type        = number
  default     = null
}

variable "kyuubi_executor_memory" {
  description = "Set kyuubi executor pods memory (in GB)."
  type        = number
  default     = null
}

variable "driver_pod_template" {
  description = "Define K8s driver pod from a file accessible to the `spark-submit` process."
  type        = string
  default     = null
}

variable "executor_pod_template" {
  description = "Define K8s executor pod from a file accessible to the `spark-submit` process."
  type        = string
  default     = null
}

variable "zookeeper_units" {
  description = "Number of zookeeper units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "tls_app_name" {
  description = "Name of the application providing the `tls-certificates` interface."
  type        = string
  nullable    = false
}

variable "tls_certificates_endpoint" {
  description = "Name of the endpoint providing the `tls-certificates` interface."
  type        = string
  nullable    = false
}

variable "history_server_revision" {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  nullable    = false
}

variable "history_server_image" {
  description = "Image for spark-history-server-k8s"
  type        = map(string)
  nullable    = false
}

variable "integration_hub_revision" {
  description = "Charm revision for spark-integration-hub-k8s"
  type        = number
  nullable    = false
}

variable "kyuubi_units" {
  description = "Number of Kyuubi units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "integration_hub_image" {
  description = "Image for spark-integration-hub-k8s"
  type        = map(string)
  nullable    = false
}

variable "kyuubi_revision" {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  nullable    = false
}

variable "kyuubi_image" {
  description = "Image for kyuubi-k8s"
  type        = map(string)
  nullable    = false
}

variable "kyuubi_users_revision" {
  description = "Charm revision for postgresql-k8s (auth-db)"
  type        = number
  nullable    = false
}

variable "kyuubi_users_image" {
  description = "Image for postgresql-k8s (auth-db)"
  type        = map(string)
  nullable    = false
}

variable "kyuubi_users_size" {
  description = "Storage size for the Kyuubi users database"
  type        = string
  default     = "1G"
}


variable "metastore_revision" {
  description = "Charm revision for postgresql-k8s (metastore)"
  type        = number
  nullable    = false
}

variable "metastore_image" {
  description = "Image for postgresql-k8s (metastore)"
  type        = map(string)
  nullable    = false
}

variable "metastore_size" {
  description = "Storage size for the metastore database"
  type        = string
  default     = "10G"
}


variable "zookeeper_revision" {
  description = "Charm revision for zookeeper-k8s"
  type        = number
  nullable    = false
}

variable "zookeeper_image" {
  description = "Image for zookeeper-k8s"
  type        = map(string)
  nullable    = false
}

variable "zookeeper_size" {
  description = "Storage size for the zookeeper unit"
  type        = string
  default     = "10G"
}


variable "data_integrator_revision" {
  description = "Charm revision for data-integrator"
  type        = number
  nullable    = false
}
