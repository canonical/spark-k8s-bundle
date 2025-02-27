# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Spark Juju Model to deploy to"
  type        = string
}

variable "azure" {
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
  description = "The names of the Spark applications in the Spark Juju model."
  type        = map(string)
}
