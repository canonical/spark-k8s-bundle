# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
  default     = "spark"
}

variable "cos_model" {
  description = "The name of the Juju Model of the COS deployment"
  type        = string
  default     = "cos"
}

variable "cos_user" {
  description = "The name of the Juju user of the COS deployment."
  type        = string
  default     = "admin"
}

locals {
    endpoints = {
        dashboards = "${var.cos_user}/${var.cos_model}.grafana-dashboards"
        prometheus = "${var.cos_user}/${var.cos_model}.prometheus-receive-remote-write"
        loki = "${var.cos_user}/${var.cos_model}.loki-logging"
    }
}

