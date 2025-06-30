# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

data "juju_model" "spark" {
  name = var.model
}

resource "juju_secret" "system_users_secret" {
  model = var.model
  name  = "system_users_secret"
  value = {
    admin = var.admin_password
  }
  info = "This is the password for the default admin user."
}

resource "juju_access_secret" "system_users_secret_access" {
  model = var.model
  applications = [
    juju_application.kyuubi.name
  ]
  secret_id = juju_secret.system_users_secret.secret_id
}
