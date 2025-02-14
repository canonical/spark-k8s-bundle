data "juju_model" "identity" {
  name = var.model
}

data "juju_model" "spark"{
    name = var.spark_model
}

resource "juju_offer" "traefik_ingress" {
  model            = data.juju_model.identity.name
  application_name = juju_application.traefik-external.name
  endpoint         = "ingress"
}

resource "juju_offer" "oathkeeper_auth_proxy" {
  model            = data.juju_model.identity.name
  application_name = juju_application.oathkeeper.name
  endpoint         = "auth-proxy"
}


# authkeeper -> 
