# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    alertmanager = juju_application.alertmanager.name
    catalogue    = juju_application.catalogue.name
    grafana      = juju_application.grafana.name
    loki         = juju_application.loki.name
    prometheus   = juju_application.prometheus.name
  }
}

output "user" {
  description = "The name of the Juju user of the COS deployment."
  value       = var.cos_user
}

output "dashboards_offer" {
  value = juju_offer.grafana_dashboards.url
}

output "metrics_offer" {
  value = juju_offer.prometheus_receive_remote_write.url
}

output "logging_offer" {
  value = juju_offer.loki_logging.url
}
