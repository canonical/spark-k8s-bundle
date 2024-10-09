# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "s3_history_server" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.history_server.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_hub" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.hub.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "s3_kyuubi" {
  model      = var.model

  application {
    name = juju_application.s3.name
    endpoint = "s3-credentials"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "s3-credentials"
  }
}

resource "juju_integration" "kyuubi_metastore" {
  model      = var.model

  application {
    name = juju_application.metastore.name
    endpoint = "database"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "metastore-db"
  }
}

resource "juju_integration" "kyuubi_users" {
  model      = var.model

  application {
    name = juju_application.kyuubi_users.name
    endpoint = "database"
  }

  application {
    name = juju_application.kyuubi.name
    endpoint = "auth-db"
  }
}

resource "juju_integration" "kyuubi_service_account" {
  model      = var.model

  application {
    name = juju_application.kyuubi.name
    endpoint = "spark-service-account"
  }

  application {
    name = juju_application.hub.name
    endpoint = "spark-service-account"
  }
}



resource "juju_integration" "pushgateway_integration_hub" {
  model      = var.model

  application {
    name = var.cos_charms.pushgateway
    endpoint = "push-endpoint"
  }

  application {
    name = juju_application.integration_hub.name
    endpoint = "cos"
  }
}

resource "juju_integration" "history_server_agent_metrics" {
  model      = var.model

  application {
    name = juju_application.history_server.name
    endpoint = "metrics-endpoint"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "metrics-endpoint"
  }
}


resource "juju_integration" "history_server_agent_dashboard" {
  model      = var.model

  application {
    name = juju_application.history_server.name
    endpoint = "grafana-dashboard"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "history_server_agent_logging" {
  model      = var.model

  application {
    name = juju_application.history_server.name
    endpoint = "logging"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "logging-provider"
  }
}


resource "juju_integration" "kyuubi_agent_metrics" {
  model      = var.model

  application {
    name = juju_application.kyuubi.name
    endpoint = "metrics-endpoint"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "metrics-endpoint"
  }
}

resource "juju_integration" "kyuubi_agent_dashboards" {
  model      = var.model

  application {
    name = juju_application.kyuubi.name
    endpoint = "grafana-dashboard"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "grafana-dashboards-consumer"
  }
}

resource "juju_integration" "kyuubi_agent_logging" {
  model      = var.model

  application {
    name = juju_application.kyuubi.name
    endpoint = "logging"
  }

  application {
    name = var.cos_charms.agent
    endpoint = "logging-provider"
  }
}