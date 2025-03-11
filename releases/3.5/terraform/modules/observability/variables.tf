# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "config_repo" {
  description = "COS configuration repo URL."
  type        = string
  default     = "https://github.com/canonical/spark-k8s-bundle"
  nullable    = false
}

variable "config_grafana_path" {
  description = "Grafana dashboard path from configuration repo root."
  type        = string
  default     = "releases/3.4/resources/grafana/"
  nullable    = false
}

variable "spark_model" {
  description = "Name of the Spark Juju model."
  type        = string
  nullable    = false
}

variable "spark_charms" {
  description = "Names of the Spark applications in the Spark Juju model."
  type        = map(string)
}

variable "dashboards_offer" {
  description = "URL of the `grafana_dashboard` interface offer."
  type        = string
  nullable    = false
}

variable "metrics_offer" {
  description = "URL of the `prometheus_remote_write` interface offer."
  type        = string
  nullable    = false
}

variable "logging_offer" {
  description = "URL of the `loki_push_api` interface offer."
  type        = string
  nullable    = false
}
