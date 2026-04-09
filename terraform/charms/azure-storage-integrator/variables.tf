# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Name to give the deployed application."
  type        = string
  default     = "azure-storage-integrator"
  nullable    = false
}

variable "base" {
  description = "The operating system on which to deploy"
  type        = string
  default     = "ubuntu@22.04"
  nullable    = false
}

variable "channel" {
  description = "Channel of the charm."
  type        = string
  default     = "latest/edge" # TODO: Update to stable once we have the new release
  nullable    = false
}

variable "config" {
  description = "Map for configuration options."
  type = object({
    connection-protocol = optional(string, "abfss")
    container           = optional(string)
    credentials         = optional(string)
    endpoint            = optional(string)
    path                = optional(string)
    resource-group      = optional(string)
    storage-account     = optional(string)
  })
  default = {}
}


variable "constraints" {
  description = "String listing constraints for this application."
  type        = string
  default     = null
}

variable "model_uuid" {
  description = "Reference to an existing model uuid."
  type        = string
  nullable    = false
}


variable "revision" {
  description = "Revision number of the charm."
  type        = number
  default     = null
}

variable "units" {
  description = "Unit count."
  type        = number
  default     = 1
}
