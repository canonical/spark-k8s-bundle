# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=0.20.0"
    }
  }
}

locals {
  revisions = {
    history_server  = 94
    integration_hub = 113
    kyuubi          = 140
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
    } # rev23, spark-version: 3.5.7, release date 2026-02-27
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:c04d2d95874612883f6ead105d5f1dd74230370b23a08ea81175df81ba2e06fa"
    } # rev11, release date 2026-03-02
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:761a50ca0597825e5962c071a6575e7275e7eb04cae958d578bd7cc7f54fbb3e"
    } # rev16, spark-3.4.4, kyuubi 1.10.3 release date 2026-02-27
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

