resource "juju_application" "alertmanager" {
  name  = "alertmanager"
  trust = true
  model = var.model
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
  model = var.model
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
  model = var.model
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
  model = var.model
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
  model = var.model
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
  model = var.model
  charm {
    name    = "traefik-k8s"
    channel = "latest/stable"
  }
  config = {
    "tls-cert" : var.COS_TLS_CERT,
    "tls-key" : var.COS_TLS_KEY,
    "tls-ca" : var.COS_TLS_CA
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    configurations = "10G"
  }
}

resource "juju_offer" "prometheus-receive-remote-write" {
  model            = var.model
  application_name = juju_application.prometheus.name
  endpoint         = "receive-remote-write"
}


resource "juju_offer" "grafana-dashboards" {
  model            = var.model
  application_name = juju_application.grafana.name
  endpoint         = "grafana-dashboard"
}
