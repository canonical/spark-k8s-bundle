# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

data "juju_offer" "grafana_dashboards" {
  url = local.endpoints.dashboards
}

data "juju_offer" "prometheus" {
  url = local.endpoints.prometheus
}

resource "juju_integration" "cos_configuration_agent" {
  model      = var.model

  application {
    name = juju_application.cos_configuration.name
    endpoint = "grafana-dashboards"
  }

  application {
    name = juju_application.agent.name
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "pushgateway_scrape_config" {
  model      = var.model

  application {
    name = juju_application.pushgateway.name
    endpoint = "metrics-endpoint"
  }

  application {
    name = juju_application.scrape_config.name
    endpoint = "configurable-scrape-jobs"
  }
}

resource "juju_integration" "scrape_config_agent" {
  model      = var.model

  application {
    name = juju_application.scrape_config.name
    endpoint = "metrics-endpoint"
  }

  application {
    name = juju_application.agent.name
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "pushgateway_integration_hub" {
  model      = var.model

  application {
    name = juju_application.pushgateway.name
    endpoint = "push-endpoint"
  }

  application {
    name = var.integration_hub
    endpoint = "cos"
  }
}

resource "juju_integration" "agent_grafana_dashboards" {
  model      = var.model

  application {
    name = juju_application.agent.name
    endpoint = "grafana-dashboards-provider"
  }

  application {
    offer_url = data.juju_offer.grafana_dashboards.url
  }
}

resource "juju_integration" "agent_prometheus" {
  model      = var.model

  application {
    name = juju_application.agent.name
    endpoint = "send-remote-write"
  }

  application {
    offer_url = data.juju_offer.prometheus.url
  }
}
