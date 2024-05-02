# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "agent" {
  name = "agent"

  model      = var.model

  charm {
    name    = "grafana-agent-k8s"
    channel = "latest/stable"
    revision = 64
  }

  resources = {
      agent-image = 38
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "cos_configuration" {
  name = "cos-configuration"

  model      = var.model

  charm {
    name    = "cos-configuration-k8s"
    channel = "latest/stable"
    revision = 46
  }

  resources = {
    git-sync-image = 32
  }

  config = {
    git_branch = "main"
    git_depth  = "1"
    git_repo   = "https://github.com/canonical/spark-k8s-bundle"
    grafana_dashboards_path = "releases/3.4/resources/grafana/"
  }

  units = 1

  constraints = "arch=amd64"
}

resource "juju_application" "pushgateway" {
  name = "pushgateway"

  model      = var.model

  charm {
    name    = "prometheus-pushgateway-k8s"
    channel = "latest/stable"
    revision = 12
  }

  resources = {
    pushgateway-image = 8
  }

  units = 1

  constraints = "arch=amd64"
}

resource "juju_application" "scrape_config" {
  name = "scrape-config"

  model      = var.model

  charm {
    name    = "prometheus-scrape-config-k8s"
    channel = "latest/stable"
    revision = 47
  }

  config = {
    scrape_interval = "10s"
  }

  units = 1

  constraints = "arch=amd64"
}

