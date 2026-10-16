# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "components" {
  description = "List of the deployed applications for this component module."
  value = {
    otel_collector    = juju_application.otel_collector
    cos_configuration = juju_application.cos_configuration
    pushgateway       = juju_application.pushgateway
    scrape_config     = juju_application.scrape_config
  }
}

output "provides" {
  description = "Map of all the provided endpoints."
  value = {
    otel_collector_metrics_endpoint = {
      name     = juju_application.otel_collector.name
      endpoint = "metrics-endpoint"
    }
    otel_collector_receive_loki_logs = {
      name     = juju_application.otel_collector.name
      endpoint = "receive-loki-logs"
    }
    otel_collector_grafana_dashboards_consumer = {
      name     = juju_application.otel_collector.name
      endpoint = "grafana-dashboards-consumer"
    }
  }
}

output "requires" {
  description = "Map of the required endpoints."
  value = {
    otel_collector_grafana_dashboards_provider = {
      name     = juju_application.otel_collector.name
      endpoint = "grafana-dashboards-provider"
    }
    otel_collector_send_remote_write = {
      name     = juju_application.otel_collector.name
      endpoint = "send-remote-write"
    }
    otel_collector_send_loki_logs = {
      name     = juju_application.otel_collector.name
      endpoint = "send-loki-logs"
    }
  }
}
