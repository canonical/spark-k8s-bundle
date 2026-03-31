# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.


output "components" {
  description = "List of component modules (spark and optional addons) and their deployed charms/offers."
  value = [
    {
      name   = "spark"
      charms = module.spark.charms
      offers = module.spark.offers
    },
    {
      name   = "azure_storage"
      charms = try(module.azure_storage.charms, [])
      offers = try(module.azure_storage.offers, {})
    },
    {
      name   = "s3"
      charms = try(module.s3.charms, [])
      offers = try(module.s3.offers, {})
    },
    # {
    #   name   = "bundled_cos"
    #   charms = try(module.bundled_cos.charms, [])
    #   offers = try(module.bundled_cos.offers, {})
    # },
    # {
    #   name   = "observability"
    #   charms = try(module.observability.charms, [])
    #   offers = try(module.observability.offers, {})
    # }
  ]
}

output "offers" {
  description = "The name and url of the various offers being exposed"
  value = merge(
    concat(
      module.spark[*].offers
    )...
  )
}

output "metadata" {
  description = "Metadata of the product deployment."
  value = {
    version     = "3.4"
    deployed_at = timestamp()
    updated_at  = timestamp()
  }
}

output "models" {
  description = "Map of the models and the components deployed in each model."
  value = {
    spark = {
      model_uuid = var.model_uuid
      components = {
        spark         = module.spark
        azure_storage = try(one(module.azure_storage), null)
        s3            = try(one(module.s3), null)
        # observability = try(one(module.observability), null)
        # bundled_cos   = try(one(module.bundled_cos), null)
      }
    }
  }
}
