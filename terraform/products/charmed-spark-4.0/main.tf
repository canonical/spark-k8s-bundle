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
  revision    = var.ssc_revision
  units       = 1

}

module "kyuubi_users" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/postgresql-k8s-operator//terraform?ref=rev774"
  model_uuid = local.model_uuid

  app_name           = "kyuubi-users"
  base               = "ubuntu@22.04"
  channel            = "14/stable"
  constraints        = "arch=amd64"
  revision           = var.kyuubi_users_revision
  resources          = var.kyuubi_users_image != null ? { postgresql-image = var.kyuubi_users_image } : null
  storage_directives = { pgdata = var.kyuubi_users_size }
  units              = 1
}

module "metastore" {
  depends_on = [juju_model.spark]
  source     = "git::https://github.com/canonical/postgresql-k8s-operator//terraform?ref=rev774"
  model_uuid = local.model_uuid

  app_name           = "metastore"
  base               = "ubuntu@22.04"
  channel            = "14/stable"
  constraints        = "arch=amd64"
  revision           = var.metastore_revision
  resources          = var.metastore_image != null ? { postgresql-image = var.metastore_image } : null
  storage_directives = { pgdata = var.metastore_size }
  units              = 1
}


module "zookeeper" {
  depends_on = [juju_model.spark]
  source     = "../../charms/zookeeper"
  model_uuid = local.model_uuid

  channel     = "3/stable"
  constraints = "arch=amd64"
  revision    = var.zookeeper_revision
  resources   = var.zookeeper_image != null ? { zookeeper-image = var.zookeeper_image } : null
  units       = var.zookeeper_units
}

module "data_integrator" {
  depends_on = [juju_model.spark]
  source     = "../../charms/data-integrator"
  model_uuid = local.model_uuid

  channel     = "latest/stable"
  constraints = "arch=amd64"
  revision    = var.data_integrator_revision
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

  channel = "1/stable"
  config = merge(
    var.azure_storage_config,
    {
      credentials = "secret:${juju_secret.azure_storage_secret[0].secret_id}"
    }
  )
  constraints = "arch=amd64"
  revision    = var.azure_storage_revision
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

resource "juju_secret" "s3_secret" {
  depends_on = [juju_model.spark]
  count      = var.storage_backend == "s3" ? 1 : 0
  model_uuid = local.model_uuid
  name       = "s3_secret"
  value = {
    secret-key = var.s3_secret_key
    access-key = var.s3_access_key
  }
  info = "This is the access key and secret key for the S3 storage"
}

module "s3" {
  depends_on = [juju_model.spark, juju_secret.s3_secret]
  count      = var.storage_backend == "s3" ? 1 : 0
  source     = "../../charms/s3-integrator"
  model_uuid = local.model_uuid

  channel = "2/stable"
  config = merge(
    var.s3_config,
    {
      credentials = "secret:${juju_secret.s3_secret[0].secret_id}"
    }
  )
  constraints = "arch=amd64"
  revision    = var.s3_revision
}

resource "juju_access_secret" "s3_secret_access" {
  depends_on = [juju_model.spark, juju_secret.s3_secret, module.s3]
  count      = var.storage_backend == "s3" ? 1 : 0
  model_uuid = local.model_uuid
  applications = [
    module.s3[0].application.name
  ]
  secret_id = juju_secret.s3_secret[0].secret_id
}

resource "juju_secret" "private_key_secret" {
  depends_on = [juju_model.spark]
  count      = var.tls_private_key == null ? 0 : 1
  model_uuid = local.model_uuid
  name       = "private_key_secret"
  value = {
    private-key = var.tls_private_key
  }

  info = "This secret contains the base64 encoded TLS private key."
}

resource "juju_secret" "system_users_secret" {
  depends_on = [juju_model.spark]
  count      = var.admin_password == null ? 0 : 1
  model_uuid = local.model_uuid
  name       = "system_users_secret"
  value = {
    admin = var.admin_password
  }

  info = "This secret contains password for admin user."
}

module "spark_core" {
  depends_on = [
    juju_model.spark,
    module.azure_storage,
    module.data_integrator,
    module.s3,
    module.ssc,
  ]
  source     = "../../components/spark-core"
  model_uuid = local.model_uuid
  risk       = var.spark_risk

  history_server = {
    config    = var.history_server_config
    revision  = var.history_server_revision
    resources = var.history_server_image != null ? { spark-history-server-image = var.history_server_image } : null
    track     = "4"
  }
  integration_hub = {
    config    = var.integration_hub_config
    revision  = var.integration_hub_revision
    resources = var.integration_hub_image != null ? { integration-hub-image = var.integration_hub_image } : null
  }

  # Integrations

  object_storage           = merge({ kind = "endpoint" }, length(module.s3) != 0 ? module.s3[0].provides.s3_credentials : module.azure_storage[0].provides.azure_storage_credentials)
  object_storage_interface = length(module.s3) != 0 ? module.s3[0].provides.s3_credentials.endpoint : module.azure_storage[0].provides.azure_storage_credentials.endpoint
}

module "kyuubi" {
  depends_on = [
    juju_model.spark,
    juju_secret.system_users_secret,
    juju_secret.private_key_secret,
    module.azure_storage,
    module.kyuubi_users,
    module.metastore,
    module.s3,
    module.ssc,
    module.zookeeper,
    module.spark_core,
  ]
  source     = "../../components/kyuubi"
  model_uuid = local.model_uuid
  risk       = var.spark_risk

  kyuubi = {
    config = merge(
      {
        expose-external = "loadbalancer",
      },
      length(juju_secret.private_key_secret) > 0 ? {
        tls-client-private-key = "secret:${juju_secret.private_key_secret[0].secret_id}"
      } : {},
      length(juju_secret.system_users_secret) > 0 ? {
        system-users = "secret:${juju_secret.system_users_secret[0].secret_id}"
      } : {},
      var.kyuubi_config
    )
    revision  = var.kyuubi_revision
    resources = var.kyuubi_image != null ? { kyuubi-image = var.kyuubi_image } : null
    track     = "4.0"
    units     = var.kyuubi_units
  }

  # Integrations

  spark_service_account = merge({ kind = "endpoint" }, module.spark_core.provides.integration_hub_service_account)

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

  users_db = {
    kind     = "endpoint"
    name     = module.kyuubi_users.app_name
    endpoint = module.kyuubi_users.provides.database
  }

  zookeeper = merge({ kind = "endpoint" }, module.zookeeper.provides.zookeeper)
}

resource "juju_access_secret" "private_key_secret_access" {
  depends_on = [
    juju_model.spark,
    juju_secret.private_key_secret,
    module.kyuubi
  ]
  count      = var.tls_private_key == null ? 0 : 1
  model_uuid = local.model_uuid
  applications = [
    module.kyuubi.application.name
  ]
  secret_id = juju_secret.private_key_secret[0].secret_id
}

resource "juju_access_secret" "system_users_secret_access" {
  depends_on = [
    juju_model.spark,
    juju_secret.system_users_secret,
    module.kyuubi
  ]
  count      = var.admin_password == null ? 0 : 1
  model_uuid = local.model_uuid
  applications = [
    module.kyuubi.application.name
  ]
  secret_id = juju_secret.system_users_secret[0].secret_id
}

module "observability" {
  depends_on = [juju_model.spark, module.spark_core, module.kyuubi]
  count      = var.cos_offers == null ? 0 : 1
  source     = "../../components/observability"
  model_uuid = local.model_uuid

  dashboards_offer = var.cos_offers.dashboard
  logging_offer    = var.cos_offers.logging
  metrics_offer    = var.cos_offers.metrics

  cos_configuration = { revision = var.cos_configuration_revision }
  grafana_agent = {
    revision = var.grafana_agent_revision
    resource = var.grafana_agent_image != null ? { agent-image = var.grafana_agent_image } : null
  }
  pushgateway = {
    revision = var.pushgateway_revision
    resource = var.pushgateway_image != null ? { pushgateway-image = var.pushgateway_image } : null
  }
  scrape_config = { revision = var.scrape_config_revision }

  history_server_dashboard_endpoint = module.spark_core.provides.history_server_dashboard
  history_server_logging_endpoint   = module.spark_core.requires.history_server_logging
  history_server_metrics_endpoint   = module.spark_core.provides.history_server_metrics
  integration_hub_cos_endpoint      = module.spark_core.requires.integration_hub_cos
  integration_hub_logging_endpoint  = module.spark_core.requires.integration_hub_logging
  kyuubi_dashboard_endpoint         = module.kyuubi.provides.kyuubi_dashboard
  kyuubi_logging_endpoint           = module.kyuubi.requires.kyuubi_logging
  kyuubi_metrics_endpoint           = module.kyuubi.provides.kyuubi_metrics
}
