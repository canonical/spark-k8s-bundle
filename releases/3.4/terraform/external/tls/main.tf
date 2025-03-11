# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# This module is but a placeholder until we get an official TF module for the manual TLS operator
# For testing purpose.

terraform {
  required_version = ">=1.7.3"

  required_providers {
    juju = {
      version = ">=0.16.0"
      source  = "juju/juju"
    }
  }
}

variable "model" {
  type     = string
  nullable = false
}

variable "channel" {
  type    = string
  default = "latest/stable"
}

variable "app_name" {
  type     = string
  default  = "certificates"
  nullable = false
}

resource "juju_application" "certificates" {
  name  = var.app_name
  model = var.model

  charm {
    name    = "manual-tls-certificates"
    channel = var.channel
  }

  units = 1
  trust = true

  constraints = "arch=amd64"
}

output "app_name" {
  description = "Name of the deployed application."
  value       = juju_application.certificates.name
}

output "provides" {
  value = {
    certificates = "certificates"
  }
}
