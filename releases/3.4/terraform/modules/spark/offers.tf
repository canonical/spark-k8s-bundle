resource "juju_offer" "integration_hub" {
  model            = data.juju_model.spark.name
  application_name = juju_application.integration_hub.name
  endpoint         = "spark-service-account"
}

resource "juju_offer" "metastore" {
  model            = data.juju_model.spark.name
  application_name = juju_application.metastore.name
  endpoint         = "database"
}