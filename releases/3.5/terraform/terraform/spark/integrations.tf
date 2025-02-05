# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "kyuubi_metastore" {
  model = var.model

  application {
    name     = juju_application.metastore.name
    endpoint = "database"
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }
}

resource "juju_integration" "kyuubi_users" {
  model = var.model

  application {
    name     = juju_application.kyuubi_users.name
    endpoint = "database"
  }

  application {
    name     = juju_application.kyuubi.name
    endpoint = "auth-db"
  }
}

resource "juju_integration" "kyuubi_service_account" {
  model = var.model

  application {
    name     = juju_application.kyuubi.name
    endpoint = "spark-service-account"
  }

  application {
    name     = juju_application.hub.name
    endpoint = "spark-service-account"
  }
}

# resource "juju_integration" "kyuubi_tls" {
#   model = var.model

#   application {
#     name     = juju_application.kyuubi.name
#     endpoint = "certificates"
#   }

#   application {
#     name     = juju_application.certificates.name
#     endpoint = "certificates"
#   }
# }
