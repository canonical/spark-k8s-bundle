# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name  = "history-server"
  model = data.juju_model.spark.name

  charm {
    name     = "spark-history-server-k8s"
    channel  = "3.4/edge"
    revision = var.spark_history_server_revision
  }

  resources = var.spark_history_server_image
  #{
  #  spark-history-server-image = var.spark_history_server_image
  #}

  units = 1

  constraints = "arch=amd64"
}

resource "juju_application" "kyuubi" {
  name  = "kyuubi"
  model = data.juju_model.spark.name

  charm {
    name     = "kyuubi-k8s"
    channel  = "latest/edge"
    revision = var.kyuubi_revision
  }

  resources = var.kyuubi_image
  #{
  #  kyuubi-image = var.kyuubi_image
  #}

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
    revision = var.kyuubi_users_revision
  }

  resources = var.kyuubi_users_image
  #{
  #  postgresql-image = var.kyuubi_users_image
  #}

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
    revision = var.metastore_revision
  }

  resources = var.metastore_image
  #{
  #  postgresql-image = var.metastore_image
  #}

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
    revision = var.spark_integration_hub_revision
  }

  resources = var.spark_integration_hub_image
  #{
  #  integration-hub-image = var.spark_integration_hub_image
  #}

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "zookeeper" {
  name  = "zookeeper"
  model = data.juju_model.spark.name

  charm {
    name     = "zookeeper-k8s"
    channel  = "3/stable"
    revision = var.zookeeper_revision
  }

  resources = var.zookeeper_image
  #{
  #  zookeeper-image = var.zookeeper_image
  #}

  units       = var.zookeeper_units
  constraints = "arch=amd64"
}
