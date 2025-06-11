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
    spark_history_server     = 40
    spark_integration_hub    = 49
    kyuubi                   = 60
    kyuubi_users             = 281
    metastore                = 281
    zookeeper                = 75
    s3_integrator            = 77
    azure_storage_integrator = 12
    grafana_agent            = 104
    cos_configuration        = 67
    prometheus_pushgateway   = 16
    prometheus_scrape_config = 64
  }
  images = {
    spark_history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:04727c07bd7ce9b244cf38376e6deb7acd7eabe5579d5f043c8b4af1aa9d79a4"
    } # 3.5.1
    spark_integration_hub = {
      integration-hub-image = 5
    }
    kyuubi                = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:b91f24a14889bc4953560c5d54d1cb7c00d5bf238607dde70b02e5ce17190b5f"
    } # 3.5.4-1.9.0-22.04_edge 2025-05-02
    kyuubi_users          = {
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

