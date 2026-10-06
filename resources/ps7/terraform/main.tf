terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=1.0.0"
    }
  }
}

provider "juju" {
  controller_addresses = var.JUJU_CONTROLLER_IPS
  username             = var.JUJU_USERNAME
  password             = var.JUJU_PASSWORD
  ca_certificate       = base64decode(var.JUJU_CA_CERTIFICATE)
}


resource "juju_model" "cos" {
  name = "cos"

  config = {
    juju-http-proxy = var.HTTP_PROXY
    juju-https-proxy = var.HTTPS_PROXY
    juju-no-proxy = var.NO_PROXY
  }
}

module "cos" {
  # the source is pinned to the last commit on branch track/2 that's still compatible with Juju TF < 1.4.0. 
  # For more details, see this section in cos-lite docs: https://github.com/canonical/observability-stack/blob/track/2/terraform/cos-lite/README.md#provider--100--140
  # source       = "git::https://github.com/canonical/observability-stack//terraform/cos-lite?ref=7448dadb996835c1c0ae1d79d2f435992652d410"
  source       = "git::https://github.com/canonical/observability-stack//terraform/cos-lite?ref=track/2"
  model_uuid = juju_model.cos.uuid
}


module "spark" {
  source     = "git::https://github.com/canonical/spark-k8s-bundle//terraform/products/charmed-spark?ref=pra-414-testing-on-ps7"

  history_server_image       = "ghcr.io/canonical/charmed-spark:3.5-22.04_stable"
  integration_hub_image      = "ghcr.io/canonical/spark-integration-hub:3-22.04_stable"
  kyuubi_image               = "ghcr.io/canonical/charmed-spark-kyuubi:3.5-22.04_stable"

  spark_model_name           = "spark"

  admin_password             = "admin"

  tls_private_key            = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2d0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktrd2dnU2xBZ0VBQW9JQkFRRFRsVkJmR01CRnNrM2EKMEI1MzBMVHNkK2Fsd2NXd1BlRk1CSU5vQ2t5YzZKWDFMem01WHBQQWpia0QxaXJVVFJlRHVPa2pqNDBnVzBsQgp5Q3EzYVIrb0l0ZXdVcWd0Q0s5azIzRGwvR2cwOGRISkdZRFRqR3phbDE0RktZVy92eTZEWjljZnU1RkFjeHZSCmE1dzEvQktMc05wQnc4dUQ2a1pKbWtFQTRaTitLTU9HVlRWdlJMdnI1WXdBL21rbzBLOFk3L0VaajN0YWVBM1QKR0tMckIweWhZYkcxMnhZQUdhVitvVm41WjlLUmRLeEg0YmR6Qlp3bkNJZEdkMjhVbGNoNytqTllPWUdHbGZkeQpuYk9YR0tNSFZoci9TVDlqeVAvSGxOeUhwVTN2eEF1VWtvNFJsY2Vjenl1REJNVkN4VWhGeW9melluWG5DbTdGCjYySDUvSHczQWdNQkFBRUNnZ0VBRFFIbjhBQzRpVkJkNHU3YWdLa3ZCajZVeW1ud09sYURqRVhXd2tXbjBobW0KWm0xaDBoaVRZc29UcnIyeTRseGU3clVtZUE0eU1lUUt5K1YvWXNrdXJncCtVaE95elJuMGxuRzdMaGhuVzZIbQpNTVBGbkx2TVVWL3U0c2hidFo4T1AvdlpTTlVpSitFcnU2TXU5azZwNFRhZEpGL2lHaGtEK3pCbGdLVmRpT3JoCjhmcEZYaFNWMnBYYytseWc5dEMxWFNBNXptcGdiTUMwVm1tRFRLeDloTU95R2dvNmlyR0UyTGFwZVJOTFhXZ3MKcmtZeDJnM0dRUW1JRS9neW5rcHdlNzErUVNTQ1c5bG5adWZVb0JsVXZiazU5TkNJZlIvMUI2Y1laWjlLdjZmYgpaYWdHSm5BNE15Q1daL1NaY2locHNaZzcvb05nVFBQMkhFaXptaHRNU1FLQmdRRDU5ZDJnRC9EOWFvUjNWbFBpCk9BbXhnQnRXSVZZNUNiRDlYR1d6RXJVL3dTTGhpOXZoMUJ0eEFMZlRJRHVpQXhKOEttS2RYVTExVzZSR0RWY20KQVQwZUlNY3pxejVEdG1rTDRqY254aEJPY2plblJOdHJFWDRQbTdiTG1zZUNHRkUrVmgxR2tmVm5ZeWg5Tlo0cQpqbVlZUTdmN3A2emJxQmx4dlRFMFFzditLd0tCZ1FEWXNoRFJoWlN2Zjg4SUVsTGl1Z2IybmtIbHR2VUhKdlhqCkZ0UGVYQjFNNkUwZU5RZ2dPYmF3WVBneFJ3d0N3MmVWVGd4bnh4VFYvQU5KVXdoYmVJK1Q2bHJXbHNIMTdXc3MKT2puNHFmVm41UjMyenFxK2pKZndJZktGeXNQNXlLczRxQWlqcWl5aFZMdDg1ZFRSendEMzFyNUI2RDh0VVlxdgpvS2xwVStKQUpRS0JnUUNiYVJXSmpqL01uK3lLY2g4bmVLWDJPV3RGcXVaOEFoMkwrV1cxNS96UERkc05Gckw0CmZyTXRHRUF5d1VpeVcyeWp6SXFSd3RBRkZweFZmYmZnaGtha3M4YUd4b0twQVFIaEJKNDhXWFlNQUJIQUt4eXQKUGl2OXNsZjkwVmNYK055U2dHSWxYVnlTRW1HN0w1b09aWWp1cnpQMkFIT0dBc2NISTVVekpCREhEd0tCZ1FETApzcWVJclk5VllrbVZodFFQZVZ1dVhKb0pmSERkSmt5aUNnVmoweWRmOGtiOERGSDFLUXVJeGI3Slk4WHdtd3MyCkdNWWtqOG9RVlBRcDZ6bkI4cFRWTU1udlNveE54NzZsTnA3a0Y3QXUxL3ZRMC9sQllodzVpVS9YWVFIVVBrUmwKMzk4dktuc0Z0UWNCbzNMcFB6UGp4aVBYQktETzB3WVJqbTl5S1g1WFdRS0JnUURvSWVnejBpZlp4QzBrQ004RApPTS9IblJuWStYRW1jbkFhcGllOTFOdG1tdGZPc2RMRWM0dkk1R2FsMkQwNmdKM0NGS2cxTkxqc2Z1clFHcThNCkpheDE1bTh1Q1JEMGhTVGNjaTk3VURPS04yODFjYWlUOFFYdXZBYlIxUUxveUdJcFBkT3M0bW1oU2VudElucWgKT2h1am5WMXZ2dHVZVEtCYUw4Y2NvblBxbUE9PQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg=="

  kyuubi_config              = {"service-account": "kyuubi-user"}

  storage_backend            = "s3"
  s3_access_key              = var.S3_ACCESS_KEY
  s3_secret_key              = var.S3_SECRET_KEY
  s3_config                  = {"endpoint": var.S3_ENDPOINT_URL, "region": "eu-central-1", "bucket": "spark-tutorial", "path": "spark-events/"}

  cos_offers                 = {
    dashboard = module.cos.offers.grafana_dashboards.url
    logging   = module.cos.offers.loki_logging.url
    metrics   = module.cos.offers.prometheus_receive_remote_write.url
  }

  proxy = {
    http = var.HTTP_PROXY
    https = var.HTTPS_PROXY
    no-proxy = var.NO_PROXY
  }
}