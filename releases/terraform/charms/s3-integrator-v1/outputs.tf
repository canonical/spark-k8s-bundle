# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "Object representing the deployed application."
  value       = juju_application.s3_integrator
}

output "offers" {
  description = "Map of all offers exposed by the single charm."
  value = {
    s3_credentials = juju_offer.s3_credentials.url
  }
}


output "provides" {
  description = "Provides endpoints."
  value = {
    s3_credentials = "s3-credentials"
  }
}
