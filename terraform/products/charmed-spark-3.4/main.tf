# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_model" "spark" {
  count = (var.model_uuid == null && var.create_model == true) ? 1 : 0

  name       = var.spark_model_name
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "ssc" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/self-signed-certificates-operator//terraform?ref=rev586"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  base    = "ubuntu@24.04"
  channel = "1/stable"
  config = {
    ca-common-name = var.certificate_common_name
  }
  constraints = "arch=amd64"
  revision    = local.revisions.ssc
  units       = 1

}

module "kyuubi_users" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/postgresql-k8s-operator//terraform?ref=rev774"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  app_name    = "kyuubi-users"
  base        = "ubuntu@22.04"
  channel     = "14/stable"
  constraints = "arch=amd64"
  revision    = local.revisions.kyuubi_users
  resources = {
    postgresql-image = local.images.kyuubi_users
  }
  storage_directives = {
    pgdata = var.kyuubi_users_size
  }
  units = 1
}

module "metastore" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/postgresql-k8s-operator//terraform?ref=rev774"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  app_name    = "metastore"
  base        = "ubuntu@22.04"
  channel     = "14/stable"
  constraints = "arch=amd64"
  revision    = local.revisions.metastore
  resources = {
    postgresql-image = local.images.metastore
  }
  storage_directives = {
    pgdata = var.metastore_size
  }
  units = 1
}


module "zookeeper" {
  depends_on = [juju_model.spark]
  source     = "../../charms/zookeeper"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  base        = "ubuntu@22.04"
  channel     = "3/stable"
  constraints = "arch=amd64"
  revision    = local.revisions.zookeeper
  resources = {
    zookeeper-image = local.images.zookeeper
  }
  units = var.zookeeper_units
}

module "data_integrator" {
  depends_on = [juju_model.spark]
  source     = "../../charms/data-integrator"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  base        = "ubuntu@24.04"
  channel     = "latest/stable"
  constraints = "arch=amd64"
  revision    = local.revisions.data_integrator
}

module "azure_storage" {
  depends_on = [juju_model.spark]
  count      = var.storage_backend == "azure_storage" ? 1 : 0
  source     = "../../charms/azure-storage-integrator"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  azure_storage_secret_key = var.azure_storage_config.secret_key
  base                     = "ubuntu@22.04"
  channel                  = "latest/edge"
  config = {
    connection-protocol = var.azure_storage_config.protocol
    container           = var.azure_storage_config.container
    storage_account     = var.azure_storage_config.storage_account
  }
  constraints = "arch=amd64"
  revision    = local.revisions.azure_storage
}

module "s3" {
  depends_on = [juju_model.spark]
  count      = var.storage_backend == "s3" ? 1 : 0
  source     = "../../charms/s3-integrator-v1"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  base        = "ubuntu@22.04"
  channel     = "1/stable"
  config      = var.s3_config
  constraints = "arch=amd64"
  revision    = local.revisions.s3
}


module "spark" {
  depends_on = [
    juju_model.spark,
    module.azure_storage,
    module.data_integrator,
    module.kyuubi_users,
    module.metastore,
    module.s3,
    module.ssc,
    module.zookeeper
  ]
  source     = "../../components/spark-3.4"
  model_uuid = juju_model.spark != [] ? juju_model.spark[0].uuid : var.model_uuid

  history_server = {
    config      = var.history_server_config,
    constraints = "arch=amd64",
    revision    = var.history_server_revision != null ? var.history_server_revision : local.revisions.history_server,
    resources   = { spark-history-server-image = var.history_server_image != null ? var.history_server_image : local.images.history_server }
  }
  integration_hub = {
    config      = var.integration_hub_config,
    constraints = "arch=amd64",
    revision    = var.integration_hub_revision != null ? var.integration_hub_revision : local.revisions.integration_hub,
    resources   = { integration-hub-image = var.integration_hub_image != null ? var.integration_hub_image : local.images.integration_hub }
  }
  kyuubi = {
    config      = var.kyuubi_config,
    constraints = "arch=amd64",
    revision    = var.kyuubi_revision != null ? var.kyuubi_revision : local.revisions.kyuubi,
    resources   = { kyuubi-image = var.kyuubi_image != null ? var.kyuubi_image : local.images.kyuubi }
    units       = var.kyuubi_units
  }

  tls_endpoint = {
    name     = module.ssc.app_name
    endpoint = module.ssc.provides.certificates
  }

  metastore_endpoint = {
    name     = module.metastore.app_name
    endpoint = module.metastore.provides.database
  }

  users_db_endpoint = {
    name     = module.kyuubi_users.app_name
    endpoint = module.kyuubi_users.provides.database
  }

  zookeeper_endpoint = {
    name     = module.zookeeper.application.name
    endpoint = module.zookeeper.provides.zookeeper
  }

  data_integrator_endpoint = {
    name     = module.data_integrator.application.name
    endpoint = module.data_integrator.requires.kyuubi
  }

  object_storage_endpoint = {
    name     = module.s3 != [] ? module.s3[0].application.name : module.azure_storage[0].application.name
    endpoint = module.s3 != [] ? module.s3[0].provides.s3_credentials : module.azure_storage[0].provides.azure_storage_credentials
  }

  admin_password  = var.admin_password
  tls_private_key = var.tls_private_key


}




# module "observability" {
#   depends_on       = [module.spark, module.bundled_cos]
#   count            = var.cos.deployed == "no" ? 0 : 1
#   source           = "../../components/observability"
#   dashboards_offer = var.cos.deployed == "external" ? var.cos.offers.dashboard : one(module.bundled_cos[*].dashboards_offer)
#   logging_offer    = var.cos.deployed == "external" ? var.cos.offers.logging : one(module.bundled_cos[*].logging_offer)
#   metrics_offer    = var.cos.deployed == "external" ? var.cos.offers.metrics : one(module.bundled_cos[*].metrics_offer)
#   spark_model      = var.model
#   model_uuid       = local.active_model
#   spark_charms     = module.spark.charms

#   grafana_agent_revision     = var.grafana_agent_revision != null ? var.grafana_agent_revision : local.revisions.grafana_agent
#   cos_configuration_revision = var.cos_configuration_revision != null ? var.cos_configuration_revision : local.revisions.cos_configuration
#   pushgateway_revision       = var.pushgateway_revision != null ? var.pushgateway_revision : local.revisions.pushgateway
#   scrape_config_revision     = var.scrape_config_revision != null ? var.scrape_config_revision : local.revisions.scrape_config
# }
