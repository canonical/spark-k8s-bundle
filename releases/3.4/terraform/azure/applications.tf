# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name = "history-server"

  model      = var.model

  charm {
    name    = "spark-history-server-k8s"
    channel = "3.4/edge"
    revision = 27
  }

  resources = {
      spark-history-server-image = 12
  }

  units = 1

  constraints = "arch=amd64"

}

resource "juju_application" "azure_storage" {
  name = "azure-storage"

  model      = var.model

  charm {
    name    = "azure-storage-integrator"
    channel = "latest/edge"
    revision = 1
  }

  config = {
    container = var.azure.container
    storage-account = var.azure.storage_account
    path = "spark-events"
    connection-protocol = "abfss"
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
    revision = 18
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
    revision = 15
  }

  resources = {
      integration-hub-image = 3
  }

  units = 1
  trust = true

  constraints = "arch=amd64"

}
