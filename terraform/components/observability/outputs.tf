# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "components" {
  description = "List of the deployed applications for this component module."
  value = {
    grafana_agent     = juju_application.grafana_agent
    cos_configuration = juju_application.cos_configuration
    pushgateway       = juju_application.pushgateway
    scrape_config     = juju_application.scrape_config
  }
}

output "provides" {
  description = "Map of all the provided endpoints."
  value = {
    grafana_agent_metrics_endpoint = {
      name     = juju_application.grafana_agent.name
      endpoint = "metrics-endpoint"
    }
    grafana_agent_logging_provider = {
      name     = juju_application.grafana_agent.name
      endpoint = "logging-provider"
    }
    grafana_agent_grafana_dashboards_consumer = {
      name     = juju_application.grafana_agent.name
      endpoint = "grafana-dashboards-consumer"
    }
  }
}

output "requires" {
  description = "Map of the required endpoints."
  value = {
    grafana_agent_grafana_dashboards_provider = {
      name     = juju_application.grafana_agent.name
      endpoint = "grafana-dashboards-provider"
    }
    grafana_agent_send_remote_write = {
      name     = juju_application.grafana_agent.name
      endpoint = "send-remote-write"
    }
    grafana_agent_logging_consumer = {
      name     = juju_application.grafana_agent.name
      endpoint = "logging-consumer"
    }
  }
}
