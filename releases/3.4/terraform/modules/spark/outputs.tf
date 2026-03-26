# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    kyuubi_users    = juju_application.kyuubi_users.name
    metastore       = juju_application.metastore.name
  }
}

output "offers" {
  value = {
    metastore_database  = juju_offer.metastore
  }
}
