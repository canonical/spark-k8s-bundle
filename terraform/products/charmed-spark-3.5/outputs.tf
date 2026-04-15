# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.


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
    version     = "3.5-tf_0.0.1"
    deployed_at = timestamp()
    updated_at  = timestamp()
  }
}

output "models" {
  description = "Map of the key of the model and the components deployed in the model."
  value = {
    spark = {
      model_uuid = var.model_uuid
      components = merge(
        module.spark.components,
        {
          zookeeper = module.zookeeper.application
        },
        {
          data_integrator = module.data_integrator.application
        },
        {
          self_signed_certificates = module.ssc.app_name # TODO: expose application
        },
        {
          metastore = module.metastore.app_name # TODO: expose application
        },
        {
          kyuubi_users = module.kyuubi_users.app_name # TODO: expose application
        },
        module.azure_storage == [] ? {} : {
          azure_storage = module.azure_storage[0].application
        },
        module.s3 == [] ? {} : {
          s3 = module.s3[0].application
        },
        module.observability == [] ? {} : module.observability[0].components
      )
    }
  }
}
