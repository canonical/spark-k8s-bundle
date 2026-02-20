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
    history_server  = 81
    integration_hub = 109
    kyuubi          = 137
    kyuubi_users    = 494
    metastore       = 494
    zookeeper       = 78
    data_integrator = 178
    s3              = 145
  }
  images = {
    history_server = {
      spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:a21e7b2d697fe3cfc61986ac40e60f4e9b6e72c4c2b37b34d3e2a6f46a66a80c"
    } # rev22, spark-version: 3.5.5 
    integration_hub = {
      integration-hub-image = "ghcr.io/canonical/spark-integration-hub@sha256:2e31e78ac9eb9509d2cbbc233fbb62efe34966b8f9bcf5d862e17e7182637c7e"
    } # rev10
    kyuubi = {
      kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:9f19a582852e1e7fdfda78bea2151c5dfed9aa6a1147208eff49f3892abc6da4"
    } # rev15, spark-3.5.5, kyuubi 1.10.2
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

