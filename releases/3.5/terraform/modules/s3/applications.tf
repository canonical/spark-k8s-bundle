# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "s3" {
  name  = "s3"
  model = data.juju_model.spark.name
  charm {
    name     = "s3-integrator"
    channel  = "1/stable"
    revision = var.s3_revision
  }
  config = {
    path     = "spark-events"
    bucket   = var.s3.bucket
    endpoint = var.s3.endpoint
    region   = var.s3.region
  }
  units       = 1
  constraints = "arch=amd64"
}
