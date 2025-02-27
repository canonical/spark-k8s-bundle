# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "agent" {
  name  = "agent"
  model = data.juju_model.spark.name
  charm {
    name     = "grafana-agent-k8s"
    channel  = "latest/edge"
    revision = 103
  }
  resources = {
    agent-image = 45
  }
  units       = 1
  trust       = true
  constraints = "arch=amd64"
}

resource "juju_application" "cos_configuration" {
  name  = "cos-configuration"
  model = data.juju_model.spark.name
  charm {
    name     = "cos-configuration-k8s"
    channel  = "latest/stable"
    revision = 63
  }
  resources = {
    git-sync-image = 34
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
    name     = "prometheus-pushgateway-k8s"
    channel  = "latest/stable"
    revision = 16
  }
  resources = {
    pushgateway-image = 8
  }
  units       = 1
  constraints = "arch=amd64"
}

resource "juju_application" "scrape_config" {
  name  = "scrape-config"
  model = data.juju_model.spark.name
  charm {
    name     = "prometheus-scrape-config-k8s"
    channel  = "latest/stable"
    revision = 51
  }
  config = {
    scrape_interval = "10s"
  }
  units       = 1
  constraints = "arch=amd64"
}

