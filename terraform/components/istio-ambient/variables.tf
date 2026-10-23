# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "UUID of the Juju model where Istio Ambient is deployed"
  type        = string
  nullable    = false
}

variable "istio_ingress_k8s" {
  description = "Configuration for istio-ingress-k8s ingress gateway"
  type = object({
    channel     = optional(string, "2/stable")
    revision    = optional(number)
    units       = optional(number, 1)
    constraints = optional(string)
    config      = optional(map(string), {})
  })
  default = {}
}

variable "istio_beacon_k8s" {
  description = "Configuration for istio-beacon-k8s application"
  type = object({
    channel     = optional(string, "2/stable")
    revision    = optional(number)
    units       = optional(number, 1)
    constraints = optional(string)
    config      = optional(map(string), {})
  })
  default = {}
}

variable "certificates" {
  description = "External integration for the certificate provider application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.certificates.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.certificates.kind == "endpoint" ? (
        var.certificates.name != null && var.certificates.name != "" &&
        var.certificates.endpoint != null && var.certificates.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.certificates.kind == "offer" ? (
        var.certificates.url != null && var.certificates.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}
