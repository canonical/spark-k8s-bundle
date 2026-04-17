# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "opentelemetry_collector" {
  name       = var.opentelemetry_collector.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "opentelemetry-collector-k8s"
    channel  = var.opentelemetry_collector.channel
    revision = var.opentelemetry_collector.revision != null ? var.opentelemetry_collector.revision : local.revisions.opentelemetry_collector
  }

  constraints = var.opentelemetry_collector.constraints
  trust       = true
  units       = var.opentelemetry_collector.units
}

resource "juju_application" "cos_configuration" {
  name       = var.cos_configuration.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "cos-configuration-k8s"
    channel  = var.cos_configuration.channel
    revision = var.cos_configuration.revision != null ? var.cos_configuration.revision : local.revisions.cos_configuration
  }

  config = var.cos_configuration.config

  constraints = var.cos_configuration.constraints
  units       = var.cos_configuration.units
}

resource "juju_application" "pushgateway" {
  name       = var.pushgateway.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "prometheus-pushgateway-k8s"
    channel  = var.pushgateway.channel
    revision = var.pushgateway.revision != null ? var.pushgateway.revision : local.revisions.pushgateway
  }

  constraints        = var.pushgateway.constraints
  storage_directives = var.pushgateway.storage_directives
  units              = var.pushgateway.units
}

resource "juju_application" "scrape_config" {
  name       = var.scrape_config.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "prometheus-scrape-config-k8s"
    channel  = var.scrape_config.channel
    revision = var.scrape_config.revision != null ? var.scrape_config.revision : local.revisions.scrape_config
  }

  config      = var.scrape_config.config
  constraints = var.scrape_config.constraints
  units       = var.scrape_config.units
}

