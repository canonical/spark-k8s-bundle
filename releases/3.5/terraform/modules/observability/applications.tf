# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "grafana_agent" {
  name  = "grafana-agent"
  model = data.juju_model.spark.name
  charm {
    name     = "grafana-agent-k8s"
    channel  = "latest/stable"
    revision = var.grafana_agent_revision
  }
  units       = 1
  trust       = true
  constraints = "arch=amd64"
}

resource "juju_application" "cos_configuration" {
  name  = "cos-configuration"
  model = data.juju_model.spark.name
  charm {
    name    = "cos-configuration-k8s"
    channel = "latest/stable"
    revision = var.cos_configuration_revision
  }
  config = {
    git_branch              = "main"
    git_depth               = "1"
    git_repo                = var.config_repo
    grafana_dashboards_path = var.config_grafana_path
  }
  units       = 1
  constraints = "arch=amd64"
}

resource "juju_application" "pushgateway" {
  name  = "pushgateway"
  model = data.juju_model.spark.name
  charm {
    name    = "prometheus-pushgateway-k8s"
    channel = "latest/stable"
    revision = var.pushgateway_revision
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    pushgateway-store = "10G"
  }
}

resource "juju_application" "scrape_config" {
  name  = "scrape-config"
  model = data.juju_model.spark.name
  charm {
    name     = "prometheus-scrape-config-k8s"
    channel  = "latest/stable"
    revision = var.scrape_config_revision
  }
  config = {
    scrape_interval = "10s"
  }
  units       = 1
  constraints = "arch=amd64"
}

