# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  revisions = {
    history_server  = 96
    integration_hub = 119
    kyuubi          = 149
    kyuubi_users    = 774
    metastore       = 774
    zookeeper       = 78
    data_integrator = 362
    s3              = 330
    ssc             = 586
    azure_storage   = 270
  }
  images = {
    history_server = "ghcr.io/canonical/charmed-spark@sha256:f7f387a76ba2f3b6cfc34a35f36c0f4ae85bfa78c8c9d4bfa06ba86401b95d70"
    # rev24,  spark-version: 3.5.7, release date 16/03/2026 
    integration_hub = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
    # rev13, release date 19/03/2026
    kyuubi = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:60e81dd2e9be50d4a857ce987935341c8518c784c7de36e814fc41dd3451d58f"
    # rev19, spark-version: 3.4.4, kyuubi-version: 1.10.3, release date 17/03/2026
    kyuubi_users = "184"
    metastore    = "184"
    zookeeper    = "34"
  }
  model_uuid = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid
}

resource "terraform_data" "deployed_at" {
  input = timestamp()

  lifecycle {
    ignore_changes = [input]
  }
}
