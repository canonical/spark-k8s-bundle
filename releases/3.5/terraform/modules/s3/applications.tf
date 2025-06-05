# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "s3" {
  name  = "s3"
  model = data.juju_model.spark.name
  charm {
    name     = "s3-integrator"
    channel  = "latest/stable"
    revision = var.s3_integrator_revision
  }
  config = {
    path     = "spark-events"
    bucket   = var.s3.bucket
    endpoint = var.s3.endpoint
  }
  units       = 1
  constraints = "arch=amd64"
}
