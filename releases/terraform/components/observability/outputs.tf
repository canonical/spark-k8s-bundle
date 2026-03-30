# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = {
    grafana_agent     = juju_application.grafana_agent.name
    cos_configuration = juju_application.cos_configuration.name
    pushgateway       = juju_application.pushgateway.name
    scrape_config     = juju_application.scrape_config.name
  }
}
output "components" {
  description = "List of the deployed applications for this component module."
  value = [
    { name = juju_application.grafana_agent.name, type = "grafana_agent" },
    { name = juju_application.cos_configuration.name, type = "cos_configuration" },
    { name = juju_application.pushgateway.name, type = "pushgateway" },
    { name = juju_application.scrape_config.name, type = "scrape_config" },
  ]
}
