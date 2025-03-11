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
