# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name  = "history-server"
  model = data.juju_model.spark.name

  charm {
    name     = "spark-history-server-k8s"
    channel  = "3.4/edge"
    revision = 40
  }

  resources = {
    spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:04727c07bd7ce9b244cf38376e6deb7acd7eabe5579d5f043c8b4af1aa9d79a4" # 3.5.1
  }

  units = 1

  constraints = "arch=amd64"

}
resource "juju_application" "kyuubi" {
  name  = "kyuubi"
  model = data.juju_model.spark.name

  charm {
    name     = "kyuubi-k8s"
    channel  = "latest/edge"
    revision = 45
  }

  resources = {
    kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:3c49dfe71387bd702a30844c80c9a17a8bc8ecb99ebdee37eab4b05e44ac683f" # 3.4.2
  }

  config = {
    namespace       = data.juju_model.spark.name
    service-account = var.kyuubi_user
    expose-external = "loadbalancer"
  }

  units = 3
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "kyuubi_users" {
  name  = "kyuubi-users"
  model = data.juju_model.spark.name

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = 281
  }

  resources = {
    postgresql-image = 159
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "metastore" {
  name  = "metastore"
  model = data.juju_model.spark.name

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = 281
  }

  resources = {
    postgresql-image = 159
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "hub" {
  name  = "integration-hub"
  model = data.juju_model.spark.name

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = "latest/edge"
    revision = 46
  }

  resources = {
    integration-hub-image = 5
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "zookeeper" {
  name  = "zookeeper"
  model = data.juju_model.spark.name

  charm {
    name     = "zookeeper-k8s"
    channel  = "3/edge"
    revision = 75
  }

  resources = {
    zookeeper-image = 34
  }

  units = var.zookeeper_units

  constraints = "arch=amd64"
}
