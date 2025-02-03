# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

data "juju_offer" "grafana_dashboards" {
  url = local.endpoints.dashboards
}

data "juju_offer" "prometheus_receive_remote_write" {
  url = local.endpoints.prometheus
}

data "juju_offer" "loki_logging" {
  url = local.endpoints.loki
}

resource "juju_integration" "cos_configuration_agent" {
  model = var.spark_model

  application {
    name     = juju_application.cos_configuration.name
    endpoint = "grafana-dashboards"
  }

  application {
    name     = juju_application.agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "pushgateway_scrape_config" {
  model = var.spark_model

  application {
    name     = juju_application.pushgateway.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.scrape_config.name
    endpoint = "configurable-scrape-jobs"
  }
}

resource "juju_integration" "scrape_config_agent" {
  model = var.spark_model

  application {
    name     = juju_application.scrape_config.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.agent.name
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "agent_grafana_dashboards" {
  model = var.spark_model

  application {
    name     = juju_application.agent.name
    endpoint = "grafana-dashboards-provider"
  }

  application {
    offer_url = data.juju_offer.grafana_dashboards.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.agent.name,
      juju_application.agent.model,
      juju_application.agent.constraints,
      juju_application.agent.placement,
      juju_application.agent.charm.name,
    ]
  }
}

resource "juju_integration" "agent_prometheus" {
  model = var.spark_model

  application {
    name     = juju_application.agent.name
    endpoint = "send-remote-write"
  }

  application {
    offer_url = data.juju_offer.prometheus_receive_remote_write.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.agent.name,
      juju_application.agent.model,
      juju_application.agent.constraints,
      juju_application.agent.placement,
      juju_application.agent.charm.name,
    ]
  }
}

resource "juju_integration" "agent_loki" {
  model = var.spark_model

  application {
    name     = juju_application.agent.name
    endpoint = "logging-consumer"
  }

  application {
    offer_url = data.juju_offer.loki_logging.url
  }

  lifecycle {
    replace_triggered_by = [
      juju_application.agent.name,
      juju_application.agent.model,
      juju_application.agent.constraints,
      juju_application.agent.placement,
      juju_application.agent.charm.name,
    ]
  }
}
resource "juju_integration" "pushgateway_integration_hub" {
  model = var.spark_model

  application {
    name     = juju_application.pushgateway.name
    endpoint = "push-endpoint"
  }

  application {
    name     = var.spark_charms.hub
    endpoint = "cos"
  }
}

resource "juju_integration" "history_server_agent_dashboard" {
  model = var.spark_model

  application {
    name     = var.spark_charms.history_server
    endpoint = "grafana-dashboard"
  }

  application {
    name     = juju_application.agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "history_server_agent_logging" {
  model = var.spark_model

  application {
    name     = var.spark_charms.history_server
    endpoint = "logging"
  }

  application {
    name     = juju_application.agent.name
    endpoint = "logging-provider"
  }
}

resource "juju_integration" "history_server_agent_metrics" {
  model = var.spark_model

  application {
    name     = var.spark_charms.history_server
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.agent.name
    endpoint = "metrics-endpoint"
  }
}
