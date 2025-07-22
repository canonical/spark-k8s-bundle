# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      version = ">=0.20"
      source  = "juju/juju"
    }
  }
}

locals {
  revisions = {
    history_server    = 44
    integration_hub   = 64
    kyuubi            = 104
    kyuubi_users      = 495
    metastore         = 495
    zookeeper         = 78
    data_integrator   = 181
    s3                = 145
    azure_storage     = 15
    grafana_agent     = 121
    # TODO: bump the revision to 1/stable when the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128 
    cos_configuration = 69
    pushgateway       = 27
    scrape_config     = 67
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:99e8494070af297e9cfb6965e5216abef33539ae36fde34cbcbd2d7acb433e60"
    } # rev20 3.4 -- 30 Jan 2025
    integration_hub = {
      integration-hub-image = 5
    }
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:153eaf8be341dcea2c91277cbc2a69a1c9c48d3f7847151898ab2e5a81753ec5"
    } # rev8 3.4 -- 16 Jun 2025 
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

