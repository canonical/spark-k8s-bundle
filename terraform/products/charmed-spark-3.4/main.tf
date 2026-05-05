# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_model" "spark" {
  count = (var.model_uuid == null && var.create_model == true) ? 1 : 0

  name = var.spark_model_name
  config = {
    logging     = var.logging_config
    http-proxy  = var.proxy.http
    https-proxy = var.proxy.https
    no-proxy    = var.proxy.no-proxy
  }
}

module "ssc" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/self-signed-certificates-operator//terraform?ref=rev586"
  model_uuid = local.model_uuid

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
  model_uuid = local.model_uuid

  app_name    = "kyuubi-users"
  base        = "ubuntu@22.04"
  channel     = "14/stable"
  constraints = "arch=amd64"
  revision    = var.kyuubi_users_revision != null ? var.kyuubi_users_revision : local.revisions.kyuubi_users
  resources = {
    postgresql-image = var.kyuubi_users_image != null ? var.kyuubi_users_image : local.images.kyuubi_users
  }
  storage_directives = {
    pgdata = var.kyuubi_users_size
  }
  units = 1
}

module "metastore" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/postgresql-k8s-operator//terraform?ref=rev774"
  model_uuid = local.model_uuid

  app_name    = "metastore"
  base        = "ubuntu@22.04"
  channel     = "14/stable"
  constraints = "arch=amd64"
  revision    = var.metastore_revision != null ? var.metastore_revision : local.revisions.metastore
  resources = {
    postgresql-image = var.metastore_image != null ? var.metastore_image : local.images.metastore
  }
  storage_directives = {
    pgdata = var.metastore_size
  }
  units = 1
}


module "zookeeper" {
  depends_on = [juju_model.spark]
  source     = "../../charms/zookeeper"
  model_uuid = local.model_uuid

  channel     = "3/stable"
  constraints = "arch=amd64"
  revision    = var.zookeeper_revision != null ? var.zookeeper_revision : local.revisions.zookeeper
  resources = {
    zookeeper-image = var.zookeeper_image != null ? var.zookeeper_image : local.images.zookeeper
  }
  units = var.zookeeper_units
}

module "data_integrator" {
  depends_on = [juju_model.spark]
  source     = "../../charms/data-integrator"
  model_uuid = local.model_uuid

  channel     = "latest/stable"
  constraints = "arch=amd64"
  revision    = var.data_integrator_revision != null ? var.data_integrator_revision : local.revisions.data_integrator
}

resource "juju_secret" "azure_storage_secret" {
  depends_on = [juju_model.spark]
  count      = var.storage_backend == "azure_storage" ? 1 : 0
  model_uuid = local.model_uuid
  name       = "azure_storage_secret"
  value = {
    secret-key = var.azure_storage_secret_key
  }
  info = "This is the secret key for the Azure storage account"
}

module "azure_storage" {
  depends_on = [juju_model.spark, juju_secret.azure_storage_secret]
  count      = var.storage_backend == "azure_storage" ? 1 : 0
  source     = "../../charms/azure-storage-integrator"
  model_uuid = local.model_uuid

  channel = "latest/edge"
  config = merge(
    var.azure_storage_config,
    {
      credentials = "secret:${juju_secret.azure_storage_secret[0].secret_id}"
    }
  )
  constraints = "arch=amd64"
  revision    = var.azure_storage_revision != null ? var.azure_storage_revision : local.revisions.azure_storage
}

resource "juju_access_secret" "azure_storage_secret_access" {
  depends_on = [juju_model.spark, juju_secret.azure_storage_secret, module.azure_storage]
  count      = var.storage_backend == "azure_storage" ? 1 : 0
  model_uuid = local.model_uuid
  applications = [
    module.azure_storage[0].application.name
  ]
  secret_id = juju_secret.azure_storage_secret[0].secret_id
}

module "s3" {
  depends_on = [juju_model.spark]
  count      = var.storage_backend == "s3" ? 1 : 0
  source     = "../../charms/s3-integrator-v1"
  model_uuid = local.model_uuid

  channel     = "1/stable"
  config      = var.s3_config
  constraints = "arch=amd64"
  revision    = var.s3_revision != null ? var.s3_revision : local.revisions.s3
}

resource "juju_secret" "system_users_and_private_key_secret" {
  depends_on = [juju_model.spark]
  count      = var.tls_private_key == null && var.admin_password == null ? 0 : 1
  model_uuid = local.model_uuid
  name       = "system_users_and_private_key_secret"
  value = merge(
    var.admin_password == null ? {} : {
      admin = var.admin_password
    },
    var.tls_private_key == null ? {} : {
      private-key = var.tls_private_key
    }
  )
  info = "This secret contains password for admin user and the TLS private key."
}

module "spark" {
  depends_on = [
    juju_model.spark,
    juju_secret.system_users_and_private_key_secret,
    module.azure_storage,
    module.data_integrator,
    module.kyuubi_users,
    module.metastore,
    module.s3,
    module.ssc,
    module.zookeeper
  ]
  source     = "../../components/spark"
  model_uuid = local.model_uuid
  risk       = var.spark_risk

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
    config = merge(
      {
        expose-external = "loadbalancer",
      },
      length(juju_secret.system_users_and_private_key_secret) > 0 ? {
        system-users           = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}",
        tls-client-private-key = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
      } : {},
      var.kyuubi_config
    )
    constraints = "arch=amd64",
    revision    = var.kyuubi_revision != null ? var.kyuubi_revision : local.revisions.kyuubi,
    resources   = { kyuubi-image = var.kyuubi_image != null ? var.kyuubi_image : local.images.kyuubi }
    track       = "3.4"
    units       = var.kyuubi_units
  }

  certificates = {
    kind     = "endpoint"
    name     = module.ssc.app_name
    endpoint = module.ssc.provides.certificates
  }
  data_integrator = merge({ kind = "endpoint" }, module.data_integrator.requires.kyuubi)
  metastore = {
    kind     = "endpoint"
    name     = module.metastore.app_name
    endpoint = module.metastore.provides.database
  }
  object_storage           = merge({ kind = "endpoint" }, length(module.s3) != 0 ? module.s3[0].provides.s3_credentials : module.azure_storage[0].provides.azure_storage_credentials)
  object_storage_interface = length(module.s3) != 0 ? module.s3[0].provides.s3_credentials.endpoint : module.azure_storage[0].provides.azure_storage_credentials.endpoint
  users_db = {
    kind     = "endpoint"
    name     = module.kyuubi_users.app_name
    endpoint = module.kyuubi_users.provides.database
  }
  zookeeper = merge({ kind = "endpoint" }, module.zookeeper.provides.zookeeper)
}

resource "juju_access_secret" "system_users_and_private_key_secret_access" {
  depends_on = [
    juju_model.spark,
    juju_secret.system_users_and_private_key_secret,
    module.spark
  ]
  count      = var.tls_private_key == null && var.admin_password == null ? 0 : 1
  model_uuid = local.model_uuid
  applications = [
    module.spark.components.kyuubi.name
  ]
  secret_id = juju_secret.system_users_and_private_key_secret[0].secret_id
}

module "observability" {
  depends_on = [juju_model.spark, module.spark]
  count      = var.cos_offers == null ? 0 : 1
  source     = "../../components/observability"
  model_uuid = local.model_uuid

  dashboards_offer = var.cos_offers.dashboard
  logging_offer    = var.cos_offers.logging
  metrics_offer    = var.cos_offers.metrics

  cos_configuration = { revision = var.cos_configuration_revision }
  grafana_agent     = { revision = var.grafana_agent_revision }
  pushgateway       = { revision = var.pushgateway_revision, resource = { pushgateway-image = var.pushgateway_image } }
  scrape_config     = { revision = var.scrape_config_revision }

  history_server_dashboard_endpoint = module.spark.provides.history_server_dashboard
  history_server_logging_endpoint   = module.spark.requires.history_server_logging
  history_server_metrics_endpoint   = module.spark.provides.history_server_metrics
  integration_hub_cos_endpoint      = module.spark.requires.integration_hub_cos
  integration_hub_logging_endpoint  = module.spark.requires.integration_hub_logging
  kyuubi_dashboard_endpoint         = module.spark.provides.kyuubi_dashboard
  kyuubi_logging_endpoint           = module.spark.requires.kyuubi_logging
  kyuubi_metrics_endpoint           = module.spark.provides.kyuubi_metrics
}
