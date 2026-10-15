# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

locals {
  model_uuid = length(juju_model.spark) != 0 ? juju_model.spark[0].uuid : var.model_uuid

  # Reference to the PostgreSQL app/offer backing both the metastore and Kyuubi's
  # users database, regardless of whether this module deployed it or it's external.
  postgresql_ref = (
    var.postgresql_kind == "app" ? {
      kind     = "endpoint"
      name     = module.postgresql[0].application_name
      endpoint = module.postgresql[0].provides.database
      } : var.postgresql_kind == "endpoint" ? {
      kind     = "endpoint"
      name     = var.postgresql_name
      endpoint = "database"
      } : {
      kind = "offer"
      url  = var.postgresql_url
    }
  )
}

resource "terraform_data" "postgresql_inputs" {
  lifecycle {
    precondition {
      condition     = var.postgresql_kind != "endpoint" || coalesce(var.postgresql_name, "") != ""
      error_message = "'postgresql_name' must be set when 'postgresql_kind' is 'endpoint'."
    }

    precondition {
      condition     = var.postgresql_kind != "offer" || coalesce(var.postgresql_url, "") != ""
      error_message = "'postgresql_url' must be set when 'postgresql_kind' is 'offer'."
    }
  }
}

resource "terraform_data" "deployed_at" {
  input = timestamp()

  lifecycle {
    ignore_changes = [input]
  }
}
