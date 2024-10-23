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
    secret_key           = optional(string, "secret-key")
    path                 = optional(string, "spark-events")
  })
  default = {}
}

variable "kyuubi_user" {
  description = "Define the user to be used for running Kyuubi enginers"
  type = string
  default = "kyuubi-spark-engine"
}

variable "cos_model" {
  description = "The name of the model where cos is deployed. If null, don't deploy cos related charms."
  type = string
  nullable = true
  default = null
}

