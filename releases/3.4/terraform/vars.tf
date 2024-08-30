# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
  default     = "spark"
}

variable "storage_backend" {
  type = string
  description = "Storage backend to be used"

  validation {
    condition     = contains(["azure", "s3"], var.storage_backend)
    error_message = "Valid values for var: test_variable are (s3, azure)."
  }

  default = "s3"
}

variable "s3" {
  description = "S3 Bucket information"
  type = object({
    bucket               = optional(string, "spark-test")
    endpoint             = optional(string, "https://s3.amazonaws.com")
  })
  default = {}
}

variable "azure" {
  description = "Azure Object storage information"
  type = object({
    container            = optional(string, "spark-test")
    storage_account      = optional(string, "https://s3.amazonaws.com")
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
