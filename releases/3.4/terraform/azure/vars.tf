# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
  default     = "spark"
}

variable "azure" {
  description = "Azure Object storage information"
  type = object({
    container            = optional(string, "azurecontainer")
    storage_account      = optional(string, "azurestorageaccount")
    protocol             = optional(string, "abfss")
  })
  default = {}
}

variable "kyuubi_user" {
  description = "Define the user to be used for running Kyuubi engines"
  type = string
  default = "kyuubi-spark-engine"
}

