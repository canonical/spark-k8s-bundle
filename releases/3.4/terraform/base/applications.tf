# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name = "history-server"

  model      = var.model

  charm {
    name    = "spark-history-server-k8s"
    channel = "3.4/edge"
    revision = 30
  }

  resources = {
      spark-history-server-image = ghcr.io/canonical/charmed-spark@sha256:75a01dfca493b5a457fc7d3258daba3e9891f0408f0097f1fd189100d5de4891 # 3.4.2
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
    revision = 27
  }

  resources = {
      kyuubi-image = ghcr.io/canonical/charmed-spark-kyuubi@sha256:1395fbcb34fee2ad1c939adc0e27d5b12fc10d67457f980df548612f735b860b # 3.4.2
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

  model      = var.model

  charm {
    name    = "postgresql-k8s"
    channel = "14/stable"
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

  model      = var.model

  charm {
    name    = "spark-integration-hub-k8s"
    channel = "latest/edge"
    revision = 20
  }

  resources = {
      integration-hub-image = 3
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}
