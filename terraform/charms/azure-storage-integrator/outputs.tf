# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
# 
output "application" {
  description = "Object representing the deployed application."
  value       = juju_application.azure_storage
}

output "offers" {
  description = "Map of all offers exposed by the single charm."
  value = {
    azure_storage_credentials = juju_offer.azure_storage_credentials.url
  }
}


output "provides" {
  description = "Provides endpoints."
  value = {
    azure_storage_credentials = "azure-storage-credentials"
  }
}

