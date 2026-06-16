# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Name to give the deployed application."
  type        = string
  default     = "data-integrator"
  nullable    = false
}

variable "base" {
  description = "The operating system on which to deploy. E.g. ubuntu@22.04."
  type        = string
  default     = null
}

variable "channel" {
  description = "Channel of the charm."
  type        = string
  default     = "latest/stable"
  nullable    = false
}

variable "config" {
  description = "Map for configuration options."
  type = object({
    database-name = optional(string, "integrator")
  })
  default = {}
}

variable "constraints" {
  description = "String listing constraints for this application."
  type        = string
  default     = "arch=amd64"
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
