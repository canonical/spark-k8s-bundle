# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define spark-specific variables

variable "model" {
  description = "Name of the Juju Model to deploy to."
  type        = string
  nullable    = false
}

variable "kyuubi_user" {
  description = "User name to be used for running Kyuubi engines."
  type        = string
  nullable    = false
  default     = "kyuubi-spark-engine"
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

variable history_server_revision {
  description = "Charm revision for spark-history-server-k8s"
  type        = number
  nullable    = false
}

variable history_server_image {
  description = "Image for spark-history-server-k8s"
  type        = map(string)
  nullable    = false
}

variable integration_hub_revision {
  description = "Charm revision for spark-integration-hub-k8s"
  type        = number
  nullable    = false
}

variable integration_hub_image {
  description = "Image for spark-integration-hub-k8s"
  type        = map(string)
  nullable    = false
}

variable kyuubi_revision {
  description = "Charm revision for kyuubi-k8s"
  type        = number
  nullable    = false
}

variable kyuubi_image {
  description = "Image for kyuubi-k8s"
  type        = map(string)
  nullable    = false
}

variable kyuubi_users_revision {
  description = "Charm revision for postgresql-k8s (auth-db)"
  type        = number
  nullable    = false
}

variable kyuubi_users_image {
  description = "Image for postgresql-k8s (auth-db)"
  type        = map(string)
  nullable    = false
}

variable metastore_revision {
  description = "Charm revision for postgresql-k8s (metastore)"
  type        = number
  nullable    = false
}

variable metastore_image {
  description = "Image for postgresql-k8s (metastore)"
  type        = map(string)
  nullable    = false
}

variable zookeeper_revision {
  description = "Charm revision for zookeeper-k8s"
  type        = number
  nullable    = false
}

variable zookeeper_image {
  description = "Image for zookeeper-k8s"
  type        = map(string)
  nullable    = false
}
