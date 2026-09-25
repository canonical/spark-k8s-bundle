# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.


output "offers" {
  description = "The name and url of the various offers being exposed"
  value = merge(
    module.spark_core.offers,
    module.kyuubi.offers,
  )
}

output "metadata" {
  description = "Metadata of the product deployment."
  value = {
    version     = "3.5-tf_0.0.1"
    deployed_at = terraform_data.deployed_at.output
    updated_at  = timestamp()
  }
}

output "models" {
  description = "Map of the key of the model and the components deployed in the model."
  value = {
    spark = {
      model_uuid = local.model_uuid
      components = merge(
        module.spark_core.components,
        module.kyuubi.components,
        {
          zookeeper = module.zookeeper.application
        },
        {
          data_integrator = module.data_integrator.application
        },
        {
          self_signed_certificates = module.ssc.app_name # TODO: expose application
        },
        # metastore and kyuubi_users are aliases for the same app/offer when
        # var.postgresql.kind == "app" (a single postgresql-k8s backs both).
        {
          metastore = var.postgresql.kind == "app" ? module.postgresql[0].app_name : var.postgresql.name
        },
        {
          kyuubi_users = var.postgresql.kind == "app" ? module.postgresql[0].app_name : var.postgresql.name
        },
        length(module.azure_storage) == 0 ? {} : {
          azure_storage = module.azure_storage[0].application
        },
        length(module.s3) == 0 ? {} : {
          s3 = module.s3[0].application
        },
        length(module.observability) == 0 ? {} : module.observability[0].components
      )
    }
  }
}
