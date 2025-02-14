resource "juju_application" "traefik-internal" {
  name  = "traefik-interal"
  trust = true
  model = data.juju_model.identity.name
  charm {
    name    = "traefik-k8s"
    channel = "latest/stable"
  }
  config = {
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    configurations = "10G"
  }
}

resource "juju_application" "traefik-external" {
  name  = "traefik-external"
  trust = true
  model = data.juju_model.identity.name
  charm {
    name    = "traefik-k8s"
    channel = "latest/stable"
  }
  config = {
    "enable_experimental_forward_auth": "True"
    "tls-cert" : var.cos_tls_cert,
    "tls-key" : var.cos_tls_key,
    "tls-ca" : var.cos_tls_ca
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    configurations = "10G"
  }
}

resource "juju_application" "oathkeeper" {
  name  = "oathkeeper"
  trust = true
  model = data.juju_model.identity.name
  charm {
    name    = "oathkeeper"
    channel = "latest/stable"
  }
  config = {
    "dev" : "True",
  }
  units       = 1
  constraints = "arch=amd64"
  storage_directives = {
    configurations = "10G"
  }
}