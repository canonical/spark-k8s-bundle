# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    azure_storage = juju_application.azure_storage.name
  }
}

output "application" {
  description = "The deployed application name."
  value       = juju_application.azure_storage.name
}

output "provides" {
  description = "Relation endpoint provided by this module."
  value = {
    "azure-storage-credentials" = juju_application.azure_storage.name
  }
}
