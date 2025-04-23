# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "alertmanager" {
  name  = "alertmanager"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "alertmanager-k8s"
    channel = "latest/stable"
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    data = "10G"
  }
}

resource "juju_application" "catalogue" {
  name  = "catalogue"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "catalogue-k8s"
    channel = "latest/stable"
  }
  units       = 1
  constraints = "arch=amd64"
  config = {
    "description" : "Canonical Observability Stack Lite"
  }
}

resource "juju_application" "grafana" {
  name  = "grafana"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "grafana-k8s"
    channel = "latest/stable"
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    database = "10G"
  }
}

resource "juju_application" "loki" {
  name  = "loki"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "loki-k8s"
    channel = "latest/stable"
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    active-index-directory = "10G"
    loki-chunks            = "500G"
  }
}

resource "juju_application" "prometheus" {
  name  = "prometheus"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "prometheus-k8s"
    channel = "latest/stable"
  }
  config = {
    "metrics_retention_time" : "90d"
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    database = "500G"
  }
}

resource "juju_application" "traefik" {
  name  = "traefik"
  trust = true
  model = data.juju_model.cos.name
  charm {
    name    = "traefik-k8s"
    channel = "latest/stable"
  }
  config = {
    "tls-cert" : var.cos_tls_cert,
    "tls-key" : var.cos_tls_key,
    "tls-ca" : var.cos_tls_ca
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    configurations = "10G"
  }
}

