# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_offer" "integration_hub_service_account" {
  model_uuid       = var.model_uuid
  application_name = juju_application.integration_hub.name
  endpoints        = ["spark-service-account"]
}

resource "juju_offer" "kyuubi_jdbc" {
  model_uuid       = var.model_uuid
  application_name = juju_application.kyuubi.name
  endpoints        = ["jdbc"]
}
