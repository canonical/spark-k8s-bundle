resource "juju_model" "spark" {
  name = var.model

  cloud {
    name = "microk8s"
  }

  config = {
    logging-config              = "<root>=DEBUG"
    update-status-hook-interval = "5m"
  }
}

module "base" {
  source = "./base"

  model = juju_model.spark.name
  s3 = var.s3
}

module "cos" {
  count  = var.cos_model == null ? 0 : 1
  source = "./cos"

  model = juju_model.spark.name
  integration_hub = module.base.charms.hub
  cos_model = var.cos_model
}