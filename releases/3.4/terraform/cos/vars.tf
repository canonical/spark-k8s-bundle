# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  description = "The name of the Juju Model to deploy to"
  type        = string
  default     = "spark"
}

variable "integration_hub" {
  description = "Name of the integration hub charm deployment"
  type        = string
  default     = "integration-hub"
}

variable "history_server" {
  description = "Name of the History Server charm deployment"
  type        = string
  default     = "history-server"
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
    }
}