# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name       = var.history_server.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-history-server-k8s"
    channel  = var.history_server.channel
    revision = var.history_server.revision != null ? var.history_server.revision : local.revisions.history_server
  }

  config      = var.history_server.config
  constraints = var.history_server.constraints
  resources = merge({
    spark-history-server-image = local.images.history_server
    },
    var.history_server.resources == null ? {} : var.history_server.resources
  )
  units = var.history_server.units
}

resource "juju_application" "kyuubi" {
  name       = var.kyuubi.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "kyuubi-k8s"
    channel  = var.kyuubi.channel
    revision = var.kyuubi.revision != null ? var.kyuubi.revision : local.revisions.kyuubi
  }

  config      = var.kyuubi.config # TODO: parametrize
  constraints = var.kyuubi.constraints
  resources = merge({
    kyuubi-image = local.images.kyuubi
    },
    var.kyuubi.resources == null ? {} : var.kyuubi.resources
  )
  trust = true
  units = var.kyuubi.units

  # config = merge(
  #   {
  #     enable-dynamic-allocation  = var.enable_dynamic_allocation
  #     expose-external            = "loadbalancer"
  #     gpu-enable                 = var.kyuubi_gpu_enable
  #     gpu-engine-executors-limit = var.kyuubi_gpu_engine_executors_limit
  #     gpu-pinned-memory          = var.kyuubi_gpu_pinned_memory
  #     namespace                  = var.model_uuid # TODO: parametrize
  #     profile                    = var.kyuubi_profile
  #     service-account            = var.kyuubi_user
  #   },
  #   var.kyuubi_k8s_node_selectors == null ? {} : {
  #     k8s-node-selectors = var.kyuubi_k8s_node_selectors
  #   },
  #   var.kyuubi_loadbalancer_extra_annotations == null ? {} : {
  #     loadbalancer-extra-annotations = var.kyuubi_loadbalancer_extra_annotations
  #   },
  #   var.tls_private_key == null ? {} : {
  #     tls-client-private-key = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
  #   },
  #   var.admin_password == null ? {} : {
  #     system-users = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
  #   },
  #   var.kyuubi_executor_cores == null ? {} : {
  #     executor-cores = var.kyuubi_executor_cores
  #   },
  #   var.kyuubi_executor_memory == null ? {} : {
  #     executor-memory = var.kyuubi_executor_memory
  #   },
  #   var.kyuubi_driver_pod_template == null ? {} : {
  #     driver-pod-template = var.kyuubi_driver_pod_template
  #   },
  #   var.kyuubi_executor_pod_template == null ? {} : {
  #     executor-pod-template = var.kyuubi_executor_pod_template
  #   }
  # )

}


resource "juju_application" "integration_hub" {
  name       = var.integration_hub.app_name
  model_uuid = var.model_uuid

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = var.integration_hub.channel
    revision = var.integration_hub.revision != null ? var.integration_hub.revision : local.revisions.integration_hub
  }

  config      = var.integration_hub.config
  constraints = var.integration_hub.constraints
  resources = merge({
    integration-hub-image = local.images.integration_hub
    },
    var.integration_hub.resources == null ? {} : var.integration_hub.resources
  )
  trust = true
  units = var.integration_hub.units
  # config = merge(
  #   {
  #     enable-dynamic-allocation = var.enable_dynamic_allocation
  #   },
  #   var.driver_pod_template == null ? {} : {
  #     driver-pod-template = var.driver_pod_template
  #   },
  #   var.executor_pod_template == null ? {} : {
  #     executor-pod-template = var.executor_pod_template
  #   },
  #   var.integration_hub_monitored_service_accounts == null ? {} : {
  #     monitored-service-accounts = var.integration_hub_monitored_service_accounts
  #   }
  # )
}


