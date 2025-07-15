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
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:857f69f583fd8ee6238d1e556f749e29847ec83010c5d53f4a66388b00940da5"
    } # 3.5.4-22.04_edge 2025-05-02
    integration_hub = {
      integration-hub-image = 5
    }
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:b91f24a14889bc4953560c5d54d1cb7c00d5bf238607dde70b02e5ce17190b5f"
    } # 3.5.4-1.9.0-22.04_edge 2025-05-02
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

