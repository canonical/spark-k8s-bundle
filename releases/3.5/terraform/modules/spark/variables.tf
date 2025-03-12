# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define spark-specific variables

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
}

variable "kyuubi_user" {
  description = "Define the user to be used for running Kyuubi enginers"
  type        = string
}

variable "zookeeper_units" {
  description = "Define the number of zookeeper units. 3 units are recommended for high availability."
  type        = number
  default     = 3
  nullable    = false
}

variable "use_manual_tls" {
  type    = bool
  default = false
}
