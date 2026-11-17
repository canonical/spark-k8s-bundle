# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "components" {
  description = "List of the deployed applications for this component module."
  value = {
    charms_otel_collector    = juju_application.charms_otel_collector
    cos_configuration        = juju_application.cos_configuration
    pushgateway              = juju_application.pushgateway
    scrape_config            = juju_application.scrape_config
    workloads_otel_collector = juju_application.workloads_otel_collector
  }
}

output "provides" {
  description = "Map of all the provided endpoints."
  value = {
    workloads_otel_collector_metrics_endpoint = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "metrics-endpoint"
    }
    workloads_otel_collector_receive_loki_logs = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "receive-loki-logs"
    }
    workloads_otel_collector_grafana_dashboards_consumer = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "grafana-dashboards-consumer"
    }
    charms_otel_collector_metrics_endpoint = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "metrics-endpoint"
    }
    charms_otel_collector_receive_loki_logs = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "receive-loki-logs"
    }
    charms_otel_collector_grafana_dashboards_consumer = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "grafana-dashboards-consumer"
    }
  }
}

output "requires" {
  description = "Map of the required endpoints."
  value = {
    workloads_otel_collector_grafana_dashboards_provider = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "grafana-dashboards-provider"
    }
    workloads_otel_collector_send_remote_write = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "send-remote-write"
    }
    workloads_otel_collector_send_loki_logs = {
      name     = juju_application.workloads_otel_collector.name
      endpoint = "send-loki-logs"
    }
    charms_otel_collector_grafana_dashboards_provider = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "grafana-dashboards-provider"
    }
    charms_otel_collector_send_remote_write = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "send-remote-write"
    }
    charms_otel_collector_send_loki_logs = {
      name     = juju_application.charms_otel_collector.name
      endpoint = "send-loki-logs"
    }
  }
}
