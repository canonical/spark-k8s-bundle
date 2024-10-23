# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  value = {
    history_server = juju_application.history_server.name
    # s3 = juju_application.s3.name
    kyuubi = juju_application.kyuubi.name
    kyuubi_users = juju_application.kyuubi_users.name
    metastore = juju_application.metastore.name
    hub = juju_application.hub.name
  }
}
# TODO add other cos related endpoints 

# S3 related endpoints
output "history_server_s3" {
  value = {
    charm = juju_application.history_server.name
    endpoint = "s3-credentials"
  }
}


output "kyuubi_s3" {
  value = {
    charm = juju_application.kyuubi.name
    endpoint = "s3-credentials"
  }
}

output "hub_s3" {
  value = {
    charm = juju_application.hub.name
    endpoint = "s3-credentials"
  }
}

# Azure related endpoints
output "hub_azure" {
  value = {
    charm = juju_application.hub.name
    endpoint = "azure-credentials"
  }
}

output "history_server_azure" {
  value = {
    charm = juju_application.history_server.name
    endpoint = "azure-credentials"
  }
}



# Observability related endpoints
output "hub_obs_endpoint" {
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