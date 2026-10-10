# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

module "traefik" {
  source = "git::https://github.com/canonical/traefik-k8s-operator//terraform?ref=abd922dd7605d7d5b8cdfd0956b1efe47e5649cc"

  model_uuid         = var.model_uuid
  app_name           = var.app_name
  base               = var.base
  channel            = var.channel
  config             = var.config
  constraints        = var.constraints
  resources          = var.resources
  revision           = var.revision
  storage_directives = var.storage_directives
  units              = var.units
}
