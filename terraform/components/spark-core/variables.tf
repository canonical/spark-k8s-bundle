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

variable "service_mesh" {
  description = "External integration for the istio service mesh"
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })
  default  = null
  nullable = true

  validation {
    condition     = var.service_mesh == null || contains(["endpoint", "offer"], var.service_mesh.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.service_mesh == null ? true : (
        var.service_mesh.kind == "endpoint" ? (
          var.service_mesh.name != null && var.service_mesh.name != "" &&
          var.service_mesh.endpoint != null && var.service_mesh.endpoint != ""
        ) : true
      )
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.service_mesh == null ? true : (
        var.service_mesh.kind == "offer" ? (
          var.service_mesh.url != null && var.service_mesh.url != ""
        ) : true
      )
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "ingress" {
  description = "External integration for the history server ingress (traefik-k8s or istio-ingress-k8s)."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })
  default  = null
  nullable = true

  validation {
    condition     = var.ingress == null || contains(["endpoint", "offer"], var.ingress.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.ingress == null ? true : (
        var.ingress.kind == "endpoint" ? (
          var.ingress.name != null && var.ingress.name != "" &&
          var.ingress.endpoint != null && var.ingress.endpoint != ""
        ) : true
      )
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.ingress == null ? true : (
        var.ingress.kind == "offer" ? (
          var.ingress.url != null && var.ingress.url != ""
        ) : true
      )
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}
