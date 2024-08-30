# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  value = {
    history_server = juju_application.history_server.name
    s3 = juju_application.azure_storage.name
    kyuubi = juju_application.kyuubi.name
    kyuubi_users = juju_application.kyuubi_users.name
    metastore = juju_application.metastore.name
    hub = juju_application.hub.name
  }
}

output "cos_endpoint" {
  value = {
    charm = juju_application.hub.name
    endpoint = "cos"
  }
}

output "history_server_ingress" {
  value = {
    charm = juju_application.history_server.name
    endpoint = "ingress"
  }
}