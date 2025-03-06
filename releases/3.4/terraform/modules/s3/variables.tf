# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Spark Juju Model to deploy to"
  type        = string
}

variable "s3" {
  description = "S3 Bucket information"
  type = object({
    bucket   = optional(string, "spark-test")
    endpoint = optional(string, "https://s3.amazonaws.com")
  })
  default = {
    bucket   = "myawsbucket-f9a34"
    endpoint = "https://s3.amazonaws.com"
  }
}

variable "spark_charms" {
  description = "The names of the Spark applications in the Spark Juju model."
  type        = map(string)
}
