# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_model" "spark" {
  count      = var.create_model == true ? 1 : 0
  name       = var.model
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}


module "ssc" {
  depends_on  = [juju_model.spark]
  source      = "git::https://github.com/canonical/self-signed-certificates-operator//terraform?ref=rev326"
  model       = var.model
  app_name    = "certificates"
  channel     = "1/stable"
  revision    = 262
  constraints = "arch=arm64"
  base        = "ubuntu@24.04"
  units       = 1
  config = {
    ca-common-name = var.certificate_common_name
  }
}

module "spark" {
  depends_on                            = [juju_model.spark, module.ssc]
  source                                = "./modules/spark"
  model                                 = var.model
  kyuubi_user                           = var.kyuubi_user
  kyuubi_profile                        = var.kyuubi_profile
  admin_password                        = var.admin_password
  tls_private_key                       = var.tls_private_key
  enable_dynamic_allocation             = var.enable_dynamic_allocation
  kyuubi_k8s_node_selectors             = var.kyuubi_k8s_node_selectors
  kyuubi_loadbalancer_extra_annotations = var.kyuubi_loadbalancer_extra_annotations
  kyuubi_gpu_enable                     = var.kyuubi_gpu_enable
  kyuubi_gpu_engine_executors_limit     = var.kyuubi_gpu_engine_executors_limit
  kyuubi_gpu_pinned_memory              = var.kyuubi_gpu_pinned_memory
  kyuubi_driver_pod_template            = var.kyuubi_driver_pod_template
  kyuubi_executor_pod_template          = var.kyuubi_executor_pod_template
  kyuubi_executor_cores                 = var.kyuubi_executor_cores
  kyuubi_executor_memory                = var.kyuubi_executor_memory
  driver_pod_template                   = var.driver_pod_template
  executor_pod_template                 = var.executor_pod_template
  tls_app_name                          = module.ssc.app_name
  tls_certificates_endpoint             = module.ssc.provides.certificates
  zookeeper_units                       = var.zookeeper_units
  kyuubi_units                          = var.kyuubi_units

  history_server_revision  = var.history_server_revision != null ? var.history_server_revision : local.revisions.history_server
  history_server_image     = var.history_server_image != null ? var.history_server_image : local.images.history_server
  integration_hub_revision = var.integration_hub_revision != null ? var.integration_hub_revision : local.revisions.integration_hub
  integration_hub_image    = var.integration_hub_image != null ? var.integration_hub_image : local.images.integration_hub
  kyuubi_revision          = var.kyuubi_revision != null ? var.kyuubi_revision : local.revisions.kyuubi
  kyuubi_image             = var.kyuubi_image != null ? var.kyuubi_image : local.images.kyuubi
  kyuubi_users_revision    = var.kyuubi_users_revision != null ? var.kyuubi_users_revision : local.revisions.kyuubi_users
  kyuubi_users_image       = var.kyuubi_users_image != null ? var.kyuubi_users_image : local.images.kyuubi_users
  metastore_revision       = var.metastore_revision != null ? var.metastore_revision : local.revisions.metastore
  metastore_image          = var.metastore_image != null ? var.metastore_image : local.images.metastore
  zookeeper_revision       = var.zookeeper_revision != null ? var.zookeeper_revision : local.revisions.zookeeper
  zookeeper_image          = var.zookeeper_image != null ? var.zookeeper_image : local.images.zookeeper
  data_integrator_revision = var.data_integrator_revision != null ? var.data_integrator_revision : local.revisions.data_integrator

  kyuubi_users_size = var.kyuubi_users_size
  metastore_size    = var.metastore_size
  zookeeper_size    = var.zookeeper_size
}


module "s3" {
  depends_on   = [module.spark]
  count        = var.storage_backend == "s3" ? 1 : 0
  source       = "./modules/s3"
  model        = var.model
  spark_charms = module.spark.charms
  s3           = var.s3

  s3_revision = var.s3_revision != null ? var.s3_revision : local.revisions.s3
}

