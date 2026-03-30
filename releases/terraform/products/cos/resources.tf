# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define juju resources (model, secrets, storage)

data "juju_model" "cos" {
  name = var.model
}

resource "juju_offer" "prometheus_receive_remote_write" {
  model_uuid = data.juju_model.cos.id
  application_name = juju_application.prometheus.name
  endpoints        = ["receive-remote-write"]
}

resource "juju_offer" "grafana_dashboards" {
  model_uuid = data.juju_model.cos.id
  application_name = juju_application.grafana.name
  endpoints        = ["grafana-dashboard"]
}

resource "juju_offer" "loki_logging" {
  model_uuid = data.juju_model.cos.id
  application_name = juju_application.loki.name
  endpoints        = ["logging"]
}

