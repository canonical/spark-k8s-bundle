# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# This module is but a placeholder until we get an official TF module for the manual TLS operator
# For testing purpose.

variable "model" {
  description = "Target Juju model name (fallback if model_uuid is not provided)."
  type        = string
  default     = "spark"
}

variable "model_uuid" {
  description = "Optional existing Juju model UUID to deploy to."
  type        = string
  default     = null
}

variable "channel" {
  description = "Charm channel."
  type        = string
  default     = "latest/stable"
}

variable "app_name" {
  description = "Name of the deployed application."
  type        = string
  default     = "certificates"
}

variable "config" {
  description = "Charm configuration map."
  type        = map(string)
  default     = {}
}

variable "constraints" {
  description = "Juju constraints."
  type        = string
  default     = "arch=amd64"
}

variable "revision" {
  description = "Charm revision number."
  type        = number
  default     = null
}

variable "units" {
  description = "Number of units."
  type        = number
  default     = 1
}

locals {
  target_model_uuid = var.model_uuid != null ? var.model_uuid : data.juju_model.target[0].id
}

data "juju_model" "target" {
  count = var.model_uuid == null ? 1 : 0
  name  = var.model
}

resource "juju_application" "certificates" {
  name       = var.app_name
  model_uuid = local.target_model_uuid

  charm {
    name     = "manual-tls-certificates"
    channel  = var.channel
    revision = var.revision
  }

  config      = var.config
  constraints = var.constraints
  units       = var.units
  trust       = true
}

output "application" {
  description = "Object representing the deployed application."
  value = {
    name = juju_application.certificates.name
  }
}

output "provides" {
  value = {
    certificates = juju_application.certificates.name
  }
}
