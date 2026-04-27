# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "grafana_agent" {
  name       = var.grafana_agent.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "grafana-agent-k8s"
    channel  = var.grafana_agent.channel
    revision = var.grafana_agent.revision != null ? var.grafana_agent.revision : local.revisions.grafana_agent
  }

  constraints = var.grafana_agent.constraints
  resources   = var.grafana_agent.resources != {} ? var.grafana_agent.resources : { agent-image : local.images.grafana_agent }
  trust       = true
  units       = var.grafana_agent.units
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
  resources          = var.pushgateway.resources != {} ? var.pushgateway.resources : { pushgateway-image : local.images.pushgateway }
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

