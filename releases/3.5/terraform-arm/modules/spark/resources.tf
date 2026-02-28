# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

data "juju_model" "spark" {
  name = var.model
}

resource "juju_secret" "system_users_and_private_key_secret" {
  count = var.tls_private_key == null && var.admin_password == null ? 0 : 1
  model = var.model
  name  = "system_users_and_private_key_secret"
  value = merge(
    var.admin_password == null ? {} : {
      admin = var.admin_password
    },
    var.tls_private_key == null ? {} : {
      private-key = var.tls_private_key
    }
  )
  info = "This secret contains password for admin user and the TLS private key."
}

resource "juju_access_secret" "system_users_and_private_key_secret_access" {
  count = var.tls_private_key == null && var.admin_password == null ? 0 : 1
  model = var.model
  applications = [
    juju_application.kyuubi.name
  ]
  secret_id = juju_secret.system_users_and_private_key_secret[0].secret_id
}
