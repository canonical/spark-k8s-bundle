# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

data "juju_offer" "grafana_dashboards" {
  count = contains(keys(var.offers), "grafana_dashboard") ? 1 : 0
  url   = lookup(var.offers, "grafana_dashboard", null)
}

data "juju_offer" "prometheus_receive_remote_write" {
  count = contains(keys(var.offers), "prometheus_remote_write") ? 1 : 0
  url   = lookup(var.offers, "prometheus_remote_write", null)
}

data "juju_offer" "loki_logging" {
  count = contains(keys(var.offers), "loki_push_api") ? 1 : 0
  url   = lookup(var.offers, "loki_push_api", null)
}

## Component internal integrations

resource "juju_integration" "cos_configuration_grafana_agent" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.cos_configuration.name
    endpoint = "grafana-dashboards"
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "pushgateway_scrape_config" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.pushgateway.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.scrape_config.name
    endpoint = "configurable-scrape-jobs"
  }
}

resource "juju_integration" "scrape_config_grafana_agent" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.scrape_config.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "metrics-endpoint"
  }
}

## Cross-model COS integrations

resource "juju_integration" "grafana_agent_grafana_dashboards" {
  count      = contains(keys(var.offers), "grafana_dashboard") ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "grafana-dashboards-provider"
  }

  application {
    offer_url = data.juju_offer.grafana_dashboards[0].url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.grafana_agent.name,
      juju_application.grafana_agent.model,
      juju_application.grafana_agent.constraints,
      juju_application.grafana_agent.placement,
      juju_application.grafana_agent.charm.name,
    ]
  }
}

resource "juju_integration" "grafana_agent_prometheus" {
  count      = contains(keys(var.offers), "prometheus_remote_write") ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "send-remote-write"
  }

  application {
    offer_url = data.juju_offer.prometheus_receive_remote_write[0].url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.grafana_agent.name,
      juju_application.grafana_agent.model,
      juju_application.grafana_agent.constraints,
      juju_application.grafana_agent.placement,
      juju_application.grafana_agent.charm.name,
    ]
  }
}

resource "juju_integration" "grafana_agent_loki" {
  count      = contains(keys(var.offers), "loki_push_api") ? 1 : 0
  model_uuid = var.model_uuid

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "logging-consumer"
  }

  application {
    offer_url = data.juju_offer.loki_logging[0].url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.grafana_agent.name,
      juju_application.grafana_agent.model,
      juju_application.grafana_agent.constraints,
      juju_application.grafana_agent.placement,
      juju_application.grafana_agent.charm.name,
    ]
  }
}

## Spark components integrations

resource "juju_integration" "history_server_grafana_agent_dashboard" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_dashboard_endpoint.name
    endpoint = var.history_server_dashboard_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "history_server_grafana_agent_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_logging_endpoint.name
    endpoint = var.history_server_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "logging-provider"
  }
}

resource "juju_integration" "history_server_grafana_agent_metrics" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_metrics_endpoint.name
    endpoint = var.history_server_metrics_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "integration_hub_pushgateway" {
  model_uuid = var.model_uuid

  application {
    name     = var.integration_hub_cos_endpoint.name
    endpoint = var.integration_hub_cos_endpoint.endpoint
  }

  application {
    name     = juju_application.pushgateway.name
    endpoint = "push-endpoint"
  }
}

resource "juju_integration" "integration_hub_grafana_agent_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.integration_hub_logging_endpoint.name
    endpoint = var.integration_hub_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "logging-provider"
  }
}

resource "juju_integration" "kyuubi_grafana_agent_metrics" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_metrics_endpoint.name
    endpoint = var.kyuubi_metrics_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "kyuubi_grafana_agent_dashboards" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_dashboard_endpoint.name
    endpoint = var.kyuubi_dashboard_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "kyuubi_grafana_agent_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_logging_endpoint.name
    endpoint = var.kyuubi_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.grafana_agent.name
    endpoint = "logging-provider"
  }
}

