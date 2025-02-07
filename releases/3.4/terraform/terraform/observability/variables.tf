# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "config_repo" {
  description = "The COS configuration repo URL."
  type        = string
  default     = "https://github.com/canonical/spark-k8s-bundle"
}

variable "config_grafana_path" {
  description = "The Grafana dashboard path from configuration repo root."
  type        = string
  default     = "releases/3.4/resources/grafana/"
}

variable "spark_model" {
  description = "The name of the Spark Juju model."
  type        = string
}

variable "spark_charms" {
  description = "The names of the Spark applications in the Spark Juju model."
  type        = map(string)
}

variable "cos_model" {
  description = "The name of the COS Juju model."
  type        = string
}

variable "cos_user" {
  description = "The name of the Juju user of the COS deployment."
  type        = string
}

variable "cos_charms" {
  description = "The names of the COS applications in the COS Juju model."
  type        = map(string)
}

locals {
  endpoints = {
    dashboards = "${var.cos_user}/${var.cos_model}.grafana"
    prometheus = "${var.cos_user}/${var.cos_model}.prometheus"
    loki       = "${var.cos_user}/${var.cos_model}.loki"
  }
}

