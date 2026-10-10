# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "UUID of the Juju model where Traefik ingress is deployed."
  type        = string
  nullable    = false
}

variable "app_name" {
  description = "Name to give the deployed Traefik application."
  type        = string
  default     = "traefik"
}

variable "base" {
  description = "The operating system on which to deploy."
  type        = string
  nullable    = true
  default     = null
}

variable "channel" {
  description = "Channel that the charm is deployed from."
  type        = string
}

variable "config" {
  description = "Map of the charm configuration options."
  type        = map(string)
  default     = {}
}

variable "constraints" {
  description = "String listing constraints for this application."
  type        = string
  default     = "arch=amd64"
}

variable "resources" {
  description = "The charm's resources."
  type        = map(string)
  default     = {}
}

variable "revision" {
  description = "Revision number of the charm."
  type        = number
  default     = null
}

variable "storage_directives" {
  description = "Map of storage used by the application."
  type        = map(string)
  default     = {}
}

variable "units" {
  description = "Unit count/scale."
  type        = number
  default     = 1
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
