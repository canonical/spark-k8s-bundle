# Copyright 2026 Canonical Ltd.
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
    # TODO: Remove this pin once both of the following issue gets fixed:
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/128 
    # https://github.com/canonical/cos-configuration-k8s-operator/issues/84
    revision = optional(number, 65)
    units    = optional(number, 1)
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
    base        = optional(string, "ubuntu@24.04")
    channel     = optional(string, "2/stable")
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
    base     = optional(string, "ubuntu@24.04")
    channel  = optional(string, "2/stable")
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

variable "offers" {
  description = "Offer URLs keyed by the Juju interface each satisfies (grafana_dashboard, loki_push_api, prometheus_remote_write). An interface absent from the map is not integrated."
  type        = map(string)
  default     = {}
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
