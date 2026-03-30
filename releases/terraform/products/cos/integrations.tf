# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.




resource "juju_integration" "traefik-grafana" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.traefik.name
    endpoint = "traefik-route"
  }

  application {
    name     = juju_application.grafana.name
    endpoint = "ingress"
  }
}

resource "juju_integration" "traefik-prometheus" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.traefik.name
    endpoint = "ingress-per-unit"
  }

  application {
    name     = juju_application.prometheus.name
    endpoint = "ingress"
  }
}

resource "juju_integration" "traefik-loki" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.traefik.name
    endpoint = "ingress-per-unit"
  }

  application {
    name     = juju_application.loki.name
    endpoint = "ingress"
  }
}

resource "juju_integration" "traefik-alertmanager" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.traefik.name
    endpoint = "ingress"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "ingress"
  }
}

resource "juju_integration" "prometheus-alertmanager-alerting" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.prometheus.name
    endpoint = "alertmanager"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "alerting"
  }
}


resource "juju_integration" "grafana-prometheus-source" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-source"
  }

  application {
    name     = juju_application.prometheus.name
    endpoint = "grafana-source"
  }
}


resource "juju_integration" "grafana-loki-source" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-source"
  }

  application {
    name     = juju_application.loki.name
    endpoint = "grafana-source"
  }
}


resource "juju_integration" "grafana-alertmanager-source" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-source"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "grafana-source"
  }
}


resource "juju_integration" "loki-alertmanager" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.loki.name
    endpoint = "alertmanager"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "alerting"
  }
}


resource "juju_integration" "prometheus-traefik" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.prometheus.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.traefik.name
    endpoint = "metrics-endpoint"
  }
}


resource "juju_integration" "prometheus-alertmanager-metrics" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.prometheus.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "self-metrics-endpoint"
  }
}


resource "juju_integration" "prometheus-loki" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.prometheus.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.loki.name
    endpoint = "metrics-endpoint"
  }
}


resource "juju_integration" "prometheus-grafana" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.prometheus.name
    endpoint = "metrics-endpoint"
  }

  application {
    name     = juju_application.grafana.name
    endpoint = "metrics-endpoint"
  }
}


resource "juju_integration" "grafana-loki-dashboard" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-dashboard"
  }

  application {
    name     = juju_application.loki.name
    endpoint = "grafana-dashboard"
  }
}


resource "juju_integration" "grafana-prometheus-dashboard" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-dashboard"
  }

  application {
    name     = juju_application.prometheus.name
    endpoint = "grafana-dashboard"
  }
}


resource "juju_integration" "grafana-alertmanager-dashboard" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.grafana.name
    endpoint = "grafana-dashboard"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "grafana-dashboard"
  }
}


resource "juju_integration" "catalogue-traefik" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.catalogue.name
    endpoint = "ingress"
  }

  application {
    name     = juju_application.traefik.name
    endpoint = "ingress"
  }
}


resource "juju_integration" "catalogue-grafana" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.catalogue.name
    endpoint = "catalogue"
  }

  application {
    name     = juju_application.grafana.name
    endpoint = "catalogue"
  }
}


resource "juju_integration" "catalogue-prometheus" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.catalogue.name
    endpoint = "catalogue"
  }

  application {
    name     = juju_application.prometheus.name
    endpoint = "catalogue"
  }
}


resource "juju_integration" "catalogue-alertmanager" {
  model_uuid = data.juju_model.cos.id

  application {
    name     = juju_application.catalogue.name
    endpoint = "catalogue"
  }

  application {
    name     = juju_application.alertmanager.name
    endpoint = "catalogue"
  }
}
