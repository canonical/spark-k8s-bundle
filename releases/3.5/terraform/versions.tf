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
    history_server    = 98
    integration_hub   = 123
    kyuubi            = 160
    kyuubi_users      = 774
    metastore         = 774
    zookeeper         = 78
    data_integrator   = 362
    s3                = 330
    azure_storage     = 274
    grafana_agent     = 121
    # TODO: bump the revision to 1/stable when both of the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128 
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/84
    cos_configuration = 65
    pushgateway       = 27
    scrape_config     = 67
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:f7f387a76ba2f3b6cfc34a35f36c0f4ae85bfa78c8c9d4bfa06ba86401b95d70"
    } # rev24,  spark-version: 3.5.7, release date 16/03/2026
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:a0439da3e6a9433a0db9501c8ea7b28ba3652af9a9ec22fcc2ad1b0197d48134"
    } # rev13, release date 19/03/2026
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:21beea406001d161538b552cef2b47b86423bd899139ada263c1ef665fd89fff"
    } # rev18, spark-version: 3.5.7, kyuubi-version: 1.10.3, release date 16/03/2026
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

