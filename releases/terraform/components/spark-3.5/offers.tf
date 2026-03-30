resource "juju_offer" "integration_hub" {
  model_uuid = data.juju_model.spark.id
  application_name = juju_application.integration_hub.name
  endpoints        = ["spark-service-account"]
}

resource "juju_offer" "metastore" {
  model_uuid = data.juju_model.spark.id
  application_name = juju_application.metastore.name
  endpoints        = ["database"]
}