# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "history_server" {
  type = object({
    app_name    = optional(string, "history-server")
    base        = optional(string, "ubuntu@22.04")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(any))
    revision    = optional(number)
    track       = optional(string, "3")
    units       = optional(number, 1)
  })
  default = {}
}

variable "integration_hub" {
  type = object({
    app_name    = optional(string, "integration-hub")
    base        = optional(string, "ubuntu@22.04")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(any))
    revision    = optional(number)
    track       = optional(string, "3")
    units       = optional(number, 1)
  })
  default = {}
}

variable "model_uuid" {
  description = "Reference to an existing model uuid."
  type        = string
  nullable    = false
}

variable "object_storage" {
  description = "External integration for the object storage integrator application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.object_storage.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.object_storage.kind == "endpoint" ? (
        var.object_storage.name != null && var.object_storage.name != "" &&
        var.object_storage.endpoint != null && var.object_storage.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.object_storage.kind == "offer" ? (
        var.object_storage.url != null && var.object_storage.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "object_storage_interface" {
  description = "The interface of the object storage backend."
  type        = string

  validation {
    condition     = contains(["s3-credentials", "azure-storage-credentials"], var.object_storage_interface)
    error_message = "The only object storage interfaces supported are 's3-credentials' and 'azure-storage-credentials'."
  }
}

variable "risk" {
  description = "Component's charms risk channel"
  type        = string
  default     = "stable"

  validation {
    condition     = contains(["edge", "beta", "candidate", "stable"], var.risk)
    error_message = "'risk' can only take the following value: 'edge', 'beta', 'candidate' or 'stable'."
  }
}
