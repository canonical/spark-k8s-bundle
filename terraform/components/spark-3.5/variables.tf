# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "Reference to an existing model uuid."
  type        = string
  nullable    = false
}

variable "history_server" {
  type = object({
    app_name    = optional(string, "history-server")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "integration_hub" {
  type = object({
    app_name    = optional(string, "integration-hub")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}


variable "kyuubi" {
  type = object({
    app_name    = optional(string, "kyuubi")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3.4/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "data_integrator_endpoint" {
  description = "In-model endpoint for the data-integrator application."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "metastore_endpoint" {
  description = "In-model endpoint for the metastore (postgresql-k8s) application."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "tls_endpoint" {
  description = "In-model endpoint for the TLS certificates provider."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "users_db_endpoint" {
  description = "In-model endpoint for the Kyuubi users database (postgresql-k8s) application."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "zookeeper_endpoint" {
  description = "In-model endpoint for the ZooKeeper application."
  type = object({
    name     = string
    endpoint = string
  })
}

variable "object_storage_endpoint" {
  description = "In-model endpoint for the object storage integrator application."
  type = object({
    name     = string
    endpoint = string
  })
}

