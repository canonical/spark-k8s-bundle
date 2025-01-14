# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name  = "history-server"
  model = var.model

  charm {
    name     = "spark-history-server-k8s"
    channel  = "3.4/edge"
    revision = 33
  }

  resources = {
    spark-history-server-image = "ghcr.io/canonical/charmed-spark@sha256:04727c07bd7ce9b244cf38376e6deb7acd7eabe5579d5f043c8b4af1aa9d79a4" # 3.5.1
  }

  units       = 1
  constraints = "arch=amd64"
}

resource "juju_application" "s3" {
  name  = "s3"
  model = var.model

  charm {
    name     = "s3-integrator"
    channel  = "latest/edge"
    revision = 17
  }

  config = {
    path     = "spark-events"
    bucket   = var.s3.bucket
    endpoint = var.s3.endpoint
  }

  units       = 1
  constraints = "arch=amd64"
}


resource "juju_application" "kyuubi" {
  name  = "kyuubi"
  model = var.model

  charm {
    name     = "kyuubi-k8s"
    channel  = "latest/edge"
    revision = 29
  }

  resources = {
    kyuubi-image = "ghcr.io/canonical/charmed-spark-kyuubi@sha256:9268d19a6eef91914e874734b320fab64908faf0f7adb8856be809bc60ecd1d0"
  }

  config = {
    namespace       = var.model
    service-account = var.kyuubi_user
  }

  units       = 3
  trust       = true
  constraints = "arch=amd64"
}

resource "juju_application" "zookeeper" {
  name  = "zookeeper"
  model = var.model

  charm {
    name     = "zookeeper-k8s"
    channel  = "3/edge"
    revision = 59
  }

  resources = {
    zookeeper-image = 31
  }

  units       = 3
  constraints = "arch=amd64"
}


resource "juju_application" "kyuubi_users" {
  name  = "kyuubi-users"
  model = var.model

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = 281
  }

  resources = {
    postgresql-image = 159
  }

  units       = 1
  trust       = true
  constraints = "arch=amd64"
}

resource "juju_application" "metastore" {
  name  = "metastore"
  model = var.model

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = 281
  }

  resources = {
    postgresql-image = 159
  }

  units       = 1
  trust       = true
  constraints = "arch=amd64"
}

resource "juju_application" "hub" {
  name  = "integration-hub"
  model = var.model

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = "latest/edge"
    revision = 22
  }

  resources = {
    integration-hub-image = 3
  }

  units       = 1
  trust       = true
  constraints = "arch=amd64"
}
