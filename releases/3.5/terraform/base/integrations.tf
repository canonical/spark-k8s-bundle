# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "s3_history_server" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.history_server.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_hub" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.hub.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_kyuubi" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "kyuubi_metastore" {
  model      = var.model

  application {
    name = juju_application.metastore.name
    endpoint = "database"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }
}

resource "juju_integration" "kyuubi_users" {
  model      = var.model

  application {
    name = juju_application.kyuubi_users.name
    endpoint = "database"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "auth-db"
  }
}

resource "juju_integration" "kyuubi_service_account" {
  model      = var.model

  application {
    name = juju_application.kyuubi.name
    endpoint = "spark-service-account"
  }

  application {
    name = juju_application.hub.name
    endpoint = "spark-service-account"
  }
}

resource "juju_integration" "kyuubi_zookeeper" {
  model      = var.model

  application {
    name = juju_application.zookeeper.name
    endpoint = "zookeeper"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "zookeeper"
  }
}s