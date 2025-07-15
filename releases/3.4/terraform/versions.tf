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
    integration_hub   = 59
    kyuubi            = 102
    kyuubi_users      = 495
    metastore         = 495
    zookeeper         = 78
    data_integrator   = 181
    s3                = 145
    azure_storage     = 15
    grafana_agent     = 122
    cos_configuration = 71
    pushgateway       = 27
    scrape_config     = 67
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:aaf56fbae830756295e9547593adedae20091107497d00a10f902bb22b5c88f5"
    } # 3.4.4-22.04_edge 2025-06-30
    integration_hub = {
      integration-hub-image = 5
    }
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:96492ac6d3e1b5a43d10dcefc1e92e32585b9158256e4720e98bc827f9773133"
    } # 3.4.4-1.10.2-22.04_edge 2025-06-30
    kyuubi_users = {
      postgresql-image = 165
    }
    metastore = {
      postgresql-image = 165
    }
    zookeeper = {
      zookeeper-image = 29
    }
    # grafana_agent       = ...
    # prometheus_pushgateway = ...
  }
}

