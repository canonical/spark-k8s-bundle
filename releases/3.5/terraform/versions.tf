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
    history_server  = 47
    integration_hub = 67
    kyuubi          = 111
    kyuubi_users    = 495
    metastore       = 495
    zookeeper       = 78
    data_integrator = 179
    s3              = 145
    azure_storage   = 15
    grafana_agent   = 121
    # TODO: bump the revision to 1/stable when the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128 
    cos_configuration = 69
    pushgateway       = 27
    scrape_config     = 67
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:f1f944369108c0b0112212fb0242f3c314dfad362926c234857029f13c5de2c0"
    } # rev21, spark-version: 3.5.5 revision: c9fe483160d8aad5d23260af98c18e2653720c8e
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:fa5e73d6339b2eb137b5917771caa62bd6605284b8dfab3dafb7d6026a9a3b1a"
    } # rev6
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:e2029c6976fc5b9ee2865eced632ca42ce554039d9832af20dfa3e63113e00f7"
    } # rev11, spark-3.5.5, kyuubi 1.10.2 release date 28/07/25
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

