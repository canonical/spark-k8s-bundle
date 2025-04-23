# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

data "juju_model" "cos" {
  name = var.model
}

resource "juju_offer" "prometheus_receive_remote_write" {
  model            = data.juju_model.cos.name
  application_name = juju_application.prometheus.name
  endpoint         = "receive-remote-write"
}

resource "juju_offer" "grafana_dashboards" {
  model            = data.juju_model.cos.name
  application_name = juju_application.grafana.name
  endpoint         = "grafana-dashboard"
}

resource "juju_offer" "loki_logging" {
  model            = data.juju_model.cos.name
  application_name = juju_application.loki.name
  endpoint         = "logging"
}

