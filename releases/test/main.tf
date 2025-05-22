resource "juju_model" "cos" {
  name       = "cos"
}

module "cos" {
  depends_on = [juju_model.cos]
  source     = "../3.4/terraform/external/cos"
  model      = juju_model.cos.name
}


module "spark_deployment" {
  depends_on = [module.cos]
  source = "../3.4/terraform"
  cos = {
    external=true,
    offers={
      dashboard=module.cos.dashboards_offer,
      metrics=module.cos.metrics_offer,
      logging=module.cos.logging_offer
    }
  }
  s3 = {
    bucket="spark-test",
    endpoint="http://10.152.183.249:80"
  }
  create_model = true
}

output "charms" {
  description = "The name of the charms which are part of the deployment."
  value = merge(
    module.spark_deployment.charms, module.cos.charms
  )
}
