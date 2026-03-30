# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  revisions = {
    history_server  = 94
    integration_hub = 113
    kyuubi          = 142
    kyuubi_users    = 495
    metastore       = 495
    zookeeper       = 78
    data_integrator = 179
    s3              = 145
    azure_storage   = 15
    grafana_agent   = 121
    # TODO: bump the revision to 1/stable when both of the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/84
    cos_configuration = 65
    pushgateway       = 27
    scrape_config     = 67
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:c7eef66beaeff463fdb7b707c630c0574912df8b843d8e3169f358adee2ae706"
    }
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:c04d2d95874612883f6ead105d5f1dd74230370b23a08ea81175df81ba2e06fa"
    }
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:cdde52a4f72112ea09de11c6d21f901323619cf41015db89cb9d5742c57da303"
    }
    kyuubi_users = {
      postgresql-image = 165
    }
    metastore = {
      postgresql-image = 165
    }
    zookeeper = {
      zookeeper-image = 34
    }
  }
}
