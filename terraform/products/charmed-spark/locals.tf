# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  model_uuid = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid

  # Reference to the PostgreSQL app/offer backing both the metastore and Kyuubi's
  # users database, regardless of whether this module deployed it or it's external.
  postgresql_ref = (
    var.postgresql.kind == "app" ? {
      kind     = "endpoint"
      name     = module.postgresql[0].app_name
      endpoint = module.postgresql[0].provides.database
      } : var.postgresql.kind == "endpoint" ? {
      kind     = "endpoint"
      name     = var.postgresql.name
      endpoint = "database"
      } : {
      kind = "offer"
      url  = var.postgresql.url
    }
  )
}

resource "terraform_data" "deployed_at" {
  input = timestamp()

  lifecycle {
    ignore_changes = [input]
  }
}
