# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

data "juju_offer" "grafana_dashboards" {
  url = var.dashboards_offer
}

data "juju_offer" "prometheus_receive_remote_write" {
  url = var.metrics_offer
}

data "juju_offer" "loki_logging" {
  url = var.logging_offer
}

## Component internal integrations

resource "juju_integration" "cos_configuration_opentelemetry_collector" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.cos_configuration.name
    endpoint = "grafana-dashboards"
  }

  application {
    name     = juju_application.opentelemetry_collector.name
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

resource "juju_integration" "scrape_config_opentelemetry_collector" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.scrape_config.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "metrics-endpoint"
  }
}

## Cross-model COS integrations

resource "juju_integration" "opentelemetry_collector_grafana_dashboards" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "grafana-dashboards-provider"
  }

  application {
    offer_url = data.juju_offer.grafana_dashboards.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.opentelemetry_collector.name,
      juju_application.opentelemetry_collector.model,
      juju_application.opentelemetry_collector.constraints,
      juju_application.opentelemetry_collector.placement,
      juju_application.opentelemetry_collector.charm.name,
    ]
  }
}

resource "juju_integration" "opentelemetry_collector_prometheus" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "send-remote-write"
  }

  application {
    offer_url = data.juju_offer.prometheus_receive_remote_write.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.opentelemetry_collector.name,
      juju_application.opentelemetry_collector.model,
      juju_application.opentelemetry_collector.constraints,
      juju_application.opentelemetry_collector.placement,
      juju_application.opentelemetry_collector.charm.name,
    ]
  }
}

resource "juju_integration" "opentelemetry_collector_loki" {
  model_uuid = var.model_uuid

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "send-loki-logs"
  }

  application {
    offer_url = data.juju_offer.loki_logging.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.opentelemetry_collector.name,
      juju_application.opentelemetry_collector.model,
      juju_application.opentelemetry_collector.constraints,
      juju_application.opentelemetry_collector.placement,
      juju_application.opentelemetry_collector.charm.name,
    ]
  }
}

## Spark components integrations

resource "juju_integration" "history_server_opentelemetry_collector_dashboard" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_dashboard_endpoint.name
    endpoint = var.history_server_dashboard_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "history_server_opentelemetry_collector_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_logging_endpoint.name
    endpoint = var.history_server_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "receive-loki-logs"
  }
}

resource "juju_integration" "history_server_opentelemetry_collector_metrics" {
  model_uuid = var.model_uuid

  application {
    name     = var.history_server_metrics_endpoint.name
    endpoint = var.history_server_metrics_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
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

resource "juju_integration" "integration_hub_opentelemetry_collector_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.integration_hub_logging_endpoint.name
    endpoint = var.integration_hub_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "receive-loki-logs"
  }
}

resource "juju_integration" "kyuubi_opentelemetry_collector_metrics" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_metrics_endpoint.name
    endpoint = var.kyuubi_metrics_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "kyuubi_opentelemetry_collector_dashboards" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_dashboard_endpoint.name
    endpoint = var.kyuubi_dashboard_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "kyuubi_opentelemetry_collector_logging" {
  model_uuid = var.model_uuid

  application {
    name     = var.kyuubi_logging_endpoint.name
    endpoint = var.kyuubi_logging_endpoint.endpoint
  }

  application {
    name     = juju_application.opentelemetry_collector.name
    endpoint = "receive-loki-logs"
  }
}

