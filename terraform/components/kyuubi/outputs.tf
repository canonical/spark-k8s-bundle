# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

output "application" {
  description = "Object representing the deployed Kyuubi application."
  value       = juju_application.kyuubi
}

output "components" {
  description = "Map of the deployed applications for this component module."
  value = {
    kyuubi = juju_application.kyuubi,
  }
}

output "requires" {
  description = "Map of the requires endpoints."
  value = {
    kyuubi_auth_db = {
      name     = juju_application.kyuubi.name
      endpoint = "auth-db"
    }
    kyuubi_certificates = {
      name     = juju_application.kyuubi.name
      endpoint = "certificates"
    }
    kyuubi_logging = {
      name     = juju_application.kyuubi.name
      endpoint = "logging"
    }
    kyuubi_metastore_db = {
      name     = juju_application.kyuubi.name
      endpoint = "metastore-db"
    }
    kyuubi_zookeeper = {
      name     = juju_application.kyuubi.name
      endpoint = "zookeeper"
    }
  }
}

output "provides" {
  description = "Map of all the provides endpoints."
  value = {
    kyuubi_jdbc = {
      name     = juju_application.kyuubi.name
      endpoint = "jdbc"
    }
    kyuubi_metrics = {
      name     = juju_application.kyuubi.name
      endpoint = "metrics-endpoint"
    }
    kyuubi_dashboard = {
      name     = juju_application.kyuubi.name
      endpoint = "grafana-dashboard"
    }
  }
}

output "offers" {
  description = "Map of all offers exposed by the component's charms."
  value = {
    kyuubi_jdbc = juju_offer.kyuubi_jdbc
  }
}
