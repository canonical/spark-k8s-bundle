# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "workloads_otel_collector" {
  name       = var.workloads_otelcol.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "opentelemetry-collector-k8s"
    channel  = var.workloads_otelcol.channel
    revision = var.workloads_otelcol.revision
  }

  config      = var.workloads_otelcol.config
  constraints = var.workloads_otelcol.constraints
  resources   = var.workloads_otelcol.resources
  trust       = true
  units       = var.workloads_otelcol.units
}

resource "juju_application" "charms_otel_collector" {
  name       = var.charms_otelcol.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "opentelemetry-collector-k8s"
    channel  = var.charms_otelcol.channel
    revision = var.charms_otelcol.revision
  }

  config      = var.charms_otelcol.config
  constraints = var.charms_otelcol.constraints
  resources   = var.charms_otelcol.resources
  trust       = true
  units       = var.charms_otelcol.units
}

resource "juju_application" "cos_configuration" {
  name       = var.cos_configuration.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "cos-configuration-k8s"
    channel  = var.cos_configuration.channel
    revision = var.cos_configuration.revision
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
    revision = var.pushgateway.revision
  }

  constraints        = var.pushgateway.constraints
  resources          = var.pushgateway.resources
  storage_directives = var.pushgateway.storage_directives
  units              = var.pushgateway.units
}

resource "juju_application" "scrape_config" {
  name       = var.scrape_config.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "prometheus-scrape-config-k8s"
    channel  = var.scrape_config.channel
    revision = var.scrape_config.revision
  }

  config      = var.scrape_config.config
  constraints = var.scrape_config.constraints
  units       = var.scrape_config.units
}

