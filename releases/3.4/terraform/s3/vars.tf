# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
  default     = "spark"
}

variable "s3" {
  description = "S3 Bucket information"
  type = object({
    bucket               = optional(string, "spark-test")
    endpoint             = optional(string, "https://s3.amazonaws.com")
  })
  default = {}
}

variable "kyuubi_user" {
  description = "Define the user to be used for running Kyuubi engines"
  type = string
  default = "kyuubi-spark-engine"
}

