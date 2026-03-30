# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    s3 = juju_application.s3.name
  }
}

output "application" {
  description = "The deployed application name."
  value       = juju_application.s3.name
}

output "provides" {
  description = "Relation endpoint provided by this module."
  value = {
    "s3-credentials" = juju_application.s3.name
  }
}
