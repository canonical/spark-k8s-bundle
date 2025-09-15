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
    kyuubi          = 122
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
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:99e8494070af297e9cfb6965e5216abef33539ae36fde34cbcbd2d7acb433e60"
    } # rev20, spark-version: 3.4.4 revision: 0ac21dd9c0dc624401db73ca53fa3399562308fb
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:fa5e73d6339b2eb137b5917771caa62bd6605284b8dfab3dafb7d6026a9a3b1a"
    } # rev6
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:c284924ff55152adc9a60000939d6ec604ec156ef4f4f9c9af90ef2cc501b1de"
    } # rev13, spark-3.4.4, kyuubi 1.10.2 release date 11/09/25
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

