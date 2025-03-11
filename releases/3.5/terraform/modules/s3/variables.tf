# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "Name of the Spark Juju Model to deploy to"
  type        = string
  nullable    = false
}

variable "s3" {
  description = "S3 Bucket information"
  type = object({
    bucket   = optional(string, "spark-bucket")
    endpoint = optional(string, "https://s3.amazonaws.com")
  })
  default = {
    bucket   = "spark-bucket"
    endpoint = "https://s3.amazonaws.com"
  }
}

variable "spark_charms" {
  description = "Names of the Spark applications in the Spark Juju model."
  type        = map(string)
}
