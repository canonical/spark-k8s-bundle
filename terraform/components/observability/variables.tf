# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "Reference to an existing model uuid."
  type        = string
  nullable    = false
}

variable "cos_configuration" {
  type = object({
    app_name = optional(string, "cos-configuration")
    base     = optional(string, "ubuntu@22.04")
    channel  = optional(string, "1/stable")
    config = optional(map(string), {
      git_branch              = "main"
      git_depth               = 1
      git_repo                = "https://github.com/canonical/spark-k8s-bundle"
      grafana_dashboards_path = "resources/grafana/"
    })
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "grafana_agent" {
  type = object({
    app_name    = optional(string, "grafana-agent")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "1/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "pushgateway" {
  type = object({
    app_name    = optional(string, "pushgateway")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "1/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    storage_directives = optional(map(string), {
      pushgateway-store = "10G"
    })
    units = optional(number, 1)
  })
  default = {}
}

variable "scrape_config" {
  type = object({
    app_name = optional(string, "scrape-config")
    base     = optional(string, "ubuntu@22.04")
    channel  = optional(string, "1/stable")
    config = optional(map(string), {
      scrape_interval = "10s"
    })
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "dashboards_offer" {
  description = "URL of the `grafana_dashboard` interface offer."
  type        = string
  nullable    = false
}


variable "logging_offer" {
  description = "URL of the `loki_push_api` interface offer."
  type        = string
  nullable    = false
}

variable "metrics_offer" {
  description = "URL of the `prometheus_remote_write` interface offer."
  type        = string
  nullable    = false
}

variable "history_server_logging_endpoint" {
  description = "In-model endpoint for the History Server logging integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "history_server_metrics_endpoint" {
  description = "In-model endpoint for the History Server metrics integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "history_server_dashboard_endpoint" {
  description = "In-model endpoint for the History Server dashboard integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "integration_hub_cos_endpoint" {
  description = "In-model endpoint for the Integration Hub COS integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "integration_hub_logging_endpoint" {
  description = "In-model endpoint for the Integration Hub logging integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "kyuubi_logging_endpoint" {
  description = "In-model endpoint for the Kyuubi logging integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "kyuubi_metrics_endpoint" {
  description = "In-model endpoint for the Kyuubi metrics integration."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "kyuubi_dashboard_endpoint" {
  description = "In-model endpoint for the Kyuubi dashboard integration."
  type = object({
    name     = string
    endpoint = string
  })
}
