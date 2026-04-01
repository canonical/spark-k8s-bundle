# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "Object representing the deployed application."
  value       = juju_application.zookeeper
}

output "provides" {
  description = "Map of all the provided endpoints."
  value = {
    zookeeper = "zookeeper"
  }
}

output "requires" {
  description = "Map of all the required endpoints."
  value       = {}
}
