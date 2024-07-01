# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name = "history-server"

  model      = var.model

  charm {
    name    = "spark-history-server-k8s"
    channel = "3.4/edge"
    revision = 24
  }

  resources = {
      spark-history-server-image = 12
  }

  units = 1

  constraints = "arch=amd64"

}

resource "juju_application" "s3" {
  name = "s3"

  model      = var.model

  charm {
    name    = "s3-integrator"
    channel = "latest/edge"
    revision = 17
  }

  config = {
      path = "spark-events"
      bucket = var.s3.bucket
      endpoint = var.s3.endpoint
  }

  units = 1

  constraints = "arch=amd64"

}


resource "juju_application" "kyuubi" {

  name = "kyuubi"

  model      = var.model

  charm {
    name    = "kyuubi-k8s"
    channel = "latest/edge"
    revision = 14
  }

  resources = {
      kyuubi-image = 2
  }

  config = {
    namespace = var.model
    service-account = var.kyuubi_user
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "kyuubi_users" {
  name = "kyuubi-users"

  model      = var.model

  charm {
    name    = "postgresql-k8s"
    channel = "14/stable"
    revision = 193
  }

  resources = {
      postgresql-image = 149
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}

resource "juju_application" "metastore" {
  name = "metastore"

  model      = var.model

  charm {
    name    = "postgresql-k8s"
    channel = "14/stable"
    revision = 193
  }

  resources = {
      postgresql-image = 149
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}

resource "juju_application" "hub" {
  name = "integration-hub"

  model      = var.model

  charm {
    name    = "spark-integration-hub-k8s"
    channel = "latest/edge"
    revision = 6
  }

  resources = {
      integration-hub-image = 1
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}
