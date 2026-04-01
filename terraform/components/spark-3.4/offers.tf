# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_offer" "integration_hub" {
  model_uuid       = var.model_uuid
  application_name = juju_application.integration_hub.name
  endpoints        = ["spark-service-account"]
}
