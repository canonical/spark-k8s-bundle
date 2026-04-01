# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "components" {
  description = "Map of the deployed applications for this component module."
  value = {
    history_server  = juju_application.history_server,
    integration_hub = juju_application.integration_hub,
    kyuubi          = juju_application.kyuubi,
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
  }
}

output "provides" {
  description = "Map of all the provides endpoints."
  value = {
    integration_hub_service_account = {
      name     = juju_application.integration_hub.name
      endpoint = "spark-service-account"
    }
    kyuubi_jdbc = {
      name     = juju_application.kyuubi.name
      endpoint = "jdbc"
    }
  }
}

output "offers" {
  description = "Map of all offers exposed by the component's charms."
  value = {
    integration_hub_service_account = juju_offer.integration_hub_service_account
    kyuubi_jdbc                     = juju_offer.kyuubi_jdbc
  }
}
