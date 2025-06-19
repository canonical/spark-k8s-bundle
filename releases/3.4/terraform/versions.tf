# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

terraform {
  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=0.16.0"
    }
  }
}

locals {
  revisions = {
    history_server    = 40
    integration_hub   = 49
    kyuubi            = 87
    kyuubi_users      = 281
    metastore         = 281
    zookeeper         = 75
    data_integrator   = 161
    s3                = 77
    azure_storage     = 12
    grafana_agent     = 104
    cos_configuration = 67
    pushgateway       = 16
    scrape_config     = 64
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:1d9949dc7266d814e6483f8d9ffafeff32f66bb9939e0ab29ccfd9d5003a583a"
    } # 3.4.2
    integration_hub = {
      integration-hub-image = 5
    }
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:29c84e1693ce7b5e6cf4fcb84570a79357f9bc1e66bce59d2e0031f1314699e5"
    } # 3.4.4-1.10.1-22.04_edge 2025-05-06
    kyuubi_users = {
      postgresql-image = 159
    }
    metastore = {
      postgresql-image = 159
    }
    zookeeper = {
      zookeeper-image = 34
    }
    # grafana_agent       = ...
    # prometheus_pushgateway = ...
  }
}

