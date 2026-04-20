# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "components" {
  description = "List of the deployed applications for this component module."
  value = {
    opentelemetry_collector = juju_application.opentelemetry_collector
    cos_configuration       = juju_application.cos_configuration
    pushgateway             = juju_application.pushgateway
    scrape_config           = juju_application.scrape_config
  }
}

output "provides" {
  description = "Map of all the provided endpoints."
  value = {
    opentelemetry_collector_metrics_endpoint = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "metrics-endpoint"
    }
    opentelemetry_collector_receive_loki_logs = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "receive-loki-logs"
    }
    opentelemetry_collector_grafana_dashboards_consumer = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "grafana-dashboards-consumer"
    }
  }
}

output "requires" {
  description = "Map of the required endpoints."
  value = {
    opentelemetry_collector_grafana_dashboards_provider = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "grafana-dashboards-provider"
    }
    opentelemetry_collector_send_remote_write = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "send-remote-write"
    }
    opentelemetry_collector_send_loki_logs = {
      name     = juju_application.opentelemetry_collector.name
      endpoint = "send-loki-logs"
    }
  }
}
