# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Name to give the deployed application."
  type        = string
  default     = "zookeeper"
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
  default     = "3/stable"
  nullable    = false
}

variable "config" {
  description = "Map for configuration options."
  type        = map(string)
  default     = {}
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

variable "resources" {
  description = "Resources to attach to the application (e.g. OCI images)."
  type        = map(string)
  default     = null
}

variable "revision" {
  description = "Revision number of the charm."
  type        = number
  default     = null
}

variable "storage_size" {
  description = "Storage size for the zookeeper data."
  type        = string
  default     = "10G"
}

variable "units" {
  description = "Unit count. 3 units are recommended for high availability."
  type        = number
  default     = 3
}
