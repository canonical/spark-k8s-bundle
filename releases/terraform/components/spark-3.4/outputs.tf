# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    history_server  = juju_application.history_server.name
    kyuubi          = juju_application.kyuubi.name
    kyuubi_users    = juju_application.kyuubi_users.name
    metastore       = juju_application.metastore.name
    integration_hub = juju_application.integration_hub.name
    zookeeper       = juju_application.zookeeper.name
    certificates    = var.tls_app_name
  }
}

output "components" {
  description = "List of the deployed applications for this component module."
  value = [
    { name = juju_application.history_server.name, type = "history_server" },
    { name = juju_application.kyuubi.name, type = "kyuubi" },
    { name = juju_application.kyuubi_users.name, type = "kyuubi_users" },
    { name = juju_application.metastore.name, type = "metastore" },
    { name = juju_application.integration_hub.name, type = "integration_hub" },
    { name = juju_application.zookeeper.name, type = "zookeeper" },
  ]
}

output "offers" {
  value = {
    hub_service_account = juju_offer.integration_hub
    metastore_database  = juju_offer.metastore
  }
}
