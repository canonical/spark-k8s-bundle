# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_integration" "istio_ingress_k8s_certificates" {
  model_uuid = var.model_uuid

  application {
    name     = module.istio_ingress_k8s.app_name
    endpoint = "certificates"
  }

  application {
    name      = var.certificates.kind == "endpoint" ? var.certificates.name : null
    endpoint  = var.certificates.kind == "endpoint" ? var.certificates.endpoint : null
    offer_url = var.certificates.kind == "offer" ? var.certificates.url : null
  }
}
