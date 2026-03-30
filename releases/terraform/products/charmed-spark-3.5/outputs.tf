# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = merge(
    concat(
      module.spark[*].charms, module.azure_storage[*].charms, module.s3[*].charms, module.bundled_cos[*].charms, module.observability[*].charms
    )...
  )
}

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
    {
      name   = "bundled_cos"
      charms = try(module.bundled_cos.charms, [])
      offers = try(module.bundled_cos.offers, {})
    },
    {
      name   = "observability"
      charms = try(module.observability.charms, [])
      offers = try(module.observability.offers, {})
    }
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
