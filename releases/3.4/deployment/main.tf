
# provider "juju" {
#   controller_addresses = var.JUJU_CONTROLLER_IPS
#   username             = var.JUJU_USERNAME
#   password             = var.JUJU_PASSWORD
#   ca_certificate       = base64decode(var.JUJU_CA_CERTIFICATE)
# }


resource "juju_model" "spark" {
  name       = var.spark_model
#   credential = var.K8S_CREDENTIAL
#   cloud {
#     name = var.K8S_CLOUD
#   }
}


resource "juju_model" "cos" {
  name       = var.cos_model
#   credential = var.K8S_CREDENTIAL
#   cloud {
#     name = var.K8S_CLOUD
#   }
  depends_on = [
    juju_model.spark
  ]
}


module "cos" {
  source = "./cos"

  model = juju_model.cos.name
}

module "spark" {
  depends_on = [ module.cos ]

  source = "../terraform/spark"

  model = var.spark_model
  azure = var.azure
  cos_model = var.cos_model
}
