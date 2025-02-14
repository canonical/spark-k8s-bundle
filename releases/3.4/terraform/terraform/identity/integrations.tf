

resource "juju_integration" "traefik-oathkeeper" {
  model = data.juju_model.identity.name

  application {
    name     = juju_application.traefik-external.name
    endpoint = "experimental-forward-auth"
  }

  application {
    name     = juju_application.oathkeeper
    endpoint = "forward-auth"
  }
}


resource "juju_integration" "oathkeeper-kratos" {
  model = data.juju_model.identity.name

  application {
    name     = "kratos"
    endpoint = "kratos-info"
  }

  application {
    name     = juju_application.oathkeeper
    endpoint = "kratos-info"
  }
}




# authkeeper -> 
# traefik
