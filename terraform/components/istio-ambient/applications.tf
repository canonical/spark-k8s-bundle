# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.


# Istio Ingress: provides the entry point for external traffic into the service mesh.
# The upstream module hardcodes trust = true and does not accept base/resources,
module "istio_ingress_k8s" {
  source = "git::https://github.com/canonical/istio-ingress-k8s-operator//terraform?ref=a9ef9646aea149a00a6a7620acaf483249714d04"

  model_uuid  = var.model_uuid
  app_name    = "istio-ingress"
  channel     = var.istio_ingress_k8s.channel
  revision    = var.istio_ingress_k8s.revision
  units       = var.istio_ingress_k8s.units
  constraints = var.istio_ingress_k8s.constraints
  config      = var.istio_ingress_k8s.config
}


# Beacon: provides the in-model service mesh. It joins the Istio control plane
# natively (no Juju relation to istio-k8s).
#
# The upstream module hardcodes trust = true and does not accept base/resources.
module "istio_beacon_k8s" {
  source = "git::https://github.com/canonical/istio-beacon-k8s-operator//terraform?ref=51b204dd50392809692263f6e973d81dd9fe200a"

  model_uuid  = var.model_uuid
  app_name    = "istio-beacon-k8s"
  channel     = var.istio_beacon_k8s.channel
  revision    = var.istio_beacon_k8s.revision
  units       = var.istio_beacon_k8s.units
  constraints = var.istio_beacon_k8s.constraints
  config      = var.istio_beacon_k8s.config
}
