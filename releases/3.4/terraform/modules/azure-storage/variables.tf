# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "Name of the Spark Juju Model to deploy to"
  type        = string
  nullable    = false
}

variable "azure_storage" {
  description = "Azure Object storage information"
  type = object({
    container       = optional(string, "azurecontainer")
    storage_account = optional(string, "azurestorageaccount")
    protocol        = optional(string, "abfss")
    secret_key      = optional(string, "secret-key")
    path            = optional(string, "spark-events")
  })
  default = {}
}

variable "spark_charms" {
  description = "Names of the Spark applications in the Spark Juju model."
  type        = map(string)
}

variable "azure_storage_revision" {
  description = "Charm revision for azure-storage-integrator"
  type        = number
  nullable    = false
}
