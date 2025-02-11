# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name = "history-server"

  model = data.juju_model.spark.name

  charm {
    name     = "spark-history-server-k8s"
    channel  = "3.4/edge"
    revision = 37
  }

  resources = {
    spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:1d9949dc7266d814e6483f8d9ffafeff32f66bb9939e0ab29ccfd9d5003a583a" # 3.4.2
  }

  units = 1

  constraints = "arch=amd64"

}
resource "juju_application" "kyuubi" {

  name = "kyuubi"

  model = data.juju_model.spark.name

  charm {
    name     = "kyuubi-k8s"
    channel  = "latest/edge/fix-defer"
    revision = 37
  }

  resources = {
    kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:8bfbb020846bc74c29c454a98eb6134ae74d94814b5169c94d624bb25dfb8e22" # 3.4.2
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
  name = "kyuubi-users"

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
  name = "metastore"

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
  name = "integration-hub"

  model = data.juju_model.spark.name

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = "latest/edge"
    revision = 31
  }

  resources = {
    integration-hub-image = 5
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}

resource "juju_application" "certificates" {
  name = "self-signed-certificates"

  model = data.juju_model.spark.name

  charm {
    name     = "self-signed-certificates"
    channel  = "latest/edge"
    revision = 163
  }

  units = 1

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

  units       = 3
  constraints = "arch=amd64"
}
