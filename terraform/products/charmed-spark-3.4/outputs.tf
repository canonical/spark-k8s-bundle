# Copyright 2024 Canonical Ltd.
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
    version     = "3.4"
    deployed_at = timestamp()
    updated_at  = timestamp()
  }
}

output "models" {
  description = "Maps of the models and the components deployed in each model."
  value = [{
    model_uuid = var.model_uuid
    components = merge(concat(
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
      module.azure_storage == null ? {} : {
        azure_storage = module.azure_storage[0].application
      },
      module.s3 == null ? {} : {
        s3 = module.s3[0].application
      }
    ))
    }
  ]
}
