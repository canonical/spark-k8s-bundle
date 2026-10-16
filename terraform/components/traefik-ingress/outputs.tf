# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  description = "Name of the deployed Traefik application."
  value       = module.traefik.app_name
}

output "application" {
  description = "The deployed Traefik application."
  value       = module.traefik.application
}

output "provides" {
  description = "Map of the provides endpoints exposed by the charm."
  value       = module.traefik.provides
}

output "requires" {
  description = "Map of the requires endpoints consumed by the charm."
  value       = module.traefik.requires
}
