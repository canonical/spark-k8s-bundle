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
