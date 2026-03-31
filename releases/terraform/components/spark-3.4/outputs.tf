# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    history_server  = juju_application.history_server.name
    kyuubi          = juju_application.kyuubi.name
    integration_hub = juju_application.integration_hub.name
  }
}

output "components" {
  description = "List of the deployed applications for this component module."
  value = [
    juju_application.history_server,
    juju_application.integration_hub,
    juju_application.kyuubi,
  ]
}

output "provides" {
  description = "Map of all the provides endpoints."
  value = {
    integration_hub_spark_service_account = {
      name     = juju_application.integration_hub.name
      endpoint = "spark-service-account"
    }
    # TODO: Kyuubi
  }
}

output "requires" {
  description = "Map of the requires endpoints."
  value = {
    kyuubi_certificates = {
      name     = juju_application.kyuubi.name
      endpoint = "certificates"
    }
    kyuubi_metastore_db = {
      name     = juju_application.kyuubi.name
      endpoint = "metastore-db"
    }
    kyuubi_auth_db = {
      name     = juju_application.kyuubi.name
      endpoint = "auth-db"
    }
    kyuubi_zookeeper = {
      name     = juju_application.kyuubi.name
      endpoint = "zookeeper"
    }
    kyuubi_jdbc = {
      name     = juju_application.kyuubi.name
      endpoint = "jdbc"
    }
  }
}

output "offers" {
  value = {
    hub_service_account = juju_offer.integration_hub
  }
}
