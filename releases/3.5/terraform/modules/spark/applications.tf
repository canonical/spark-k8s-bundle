# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "history_server" {
  name  = "history-server"
  model = data.juju_model.spark.name

  charm {
    name     = "spark-history-server-k8s"
    channel  = "3/stable"
    revision = var.history_server_revision
  }

  resources = var.history_server_image
  units     = 1

  constraints = "arch=amd64"
}

resource "juju_application" "kyuubi" {
  name  = "kyuubi"
  model = data.juju_model.spark.name

  charm {
    name     = "kyuubi-k8s"
    channel  = "3.5/stable"
    revision = var.kyuubi_revision
  }

  resources = var.kyuubi_image

  config = merge(
    {
      namespace                 = data.juju_model.spark.name
      service-account           = var.kyuubi_user
      expose-external           = "loadbalancer"
      profile                   = var.kyuubi_profile
      enable-dynamic-allocation = var.enable_dynamic_allocation
    },
    var.kyuubi_k8s_node_selectors == null ? {} : {
      k8s-node-selectors = var.kyuubi_k8s_node_selectors
    },
    var.kyuubi_loadbalancer_extra_annotations == null ? {} : {
      loadbalancer-extra-annotations = var.kyuubi_loadbalancer_extra_annotations
    },
    var.tls_private_key == null ? {} : {
      tls-client-private-key = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
    },
    var.admin_password == null ? {} : {
      system-users = "secret:${juju_secret.system_users_and_private_key_secret[0].secret_id}"
    }
  )

  units = var.kyuubi_units
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "kyuubi_users" {
  name  = "kyuubi-users"
  model = data.juju_model.spark.name

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = var.kyuubi_users_revision
  }

  resources = var.kyuubi_users_image

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "metastore" {
  name  = "metastore"
  model = data.juju_model.spark.name

  charm {
    name     = "postgresql-k8s"
    channel  = "14/stable"
    revision = var.metastore_revision
  }

  resources = var.metastore_image

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "integration_hub" {
  name  = "integration-hub"
  model = data.juju_model.spark.name

  charm {
    name     = "spark-integration-hub-k8s"
    channel  = "3/stable"
    revision = var.integration_hub_revision
  }

  config = merge(
    {
      enable-dynamic-allocation = var.enable_dynamic_allocation
    },
    var.driver_pod_template == null ? {} : {
      driver-pod-template = var.driver_pod_template
    },
    var.executor_pod_template == null ? {} : {
      executor-pod-template = var.executor_pod_template
    }
  )

  resources = var.integration_hub_image

  units = 1
  trust = true

  constraints = "arch=amd64"
}

resource "juju_application" "zookeeper" {
  name  = "zookeeper"
  model = data.juju_model.spark.name

  charm {
    name     = "zookeeper-k8s"
    channel  = "3/stable"
    revision = var.zookeeper_revision
  }

  resources = var.zookeeper_image

  units       = var.zookeeper_units
  constraints = "arch=amd64"
}

resource "juju_application" "data_integrator" {
  name  = "data-integrator"
  model = data.juju_model.spark.name

  charm {
    name     = "data-integrator"
    channel  = "latest/stable"
    revision = var.data_integrator_revision
  }

  config = {
    database-name = "integrator"
  }

  units       = 1
  constraints = "arch=amd64"
}
