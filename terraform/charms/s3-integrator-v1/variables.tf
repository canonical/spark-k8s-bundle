# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Name to give the deployed application."
  type        = string
  default     = "s3-integrator"
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
  default     = "1/stable"
  nullable    = false
}

variable "config" {
  description = "Map for configuration options."
  type = object({
    attributes                          = optional(string, "")
    bucket                              = optional(string, "spark-bucket")
    endpoint                            = optional(string, "https://s3.amazonaws.com")
    experimental-delete-older-than-days = optional(number, 14)
    path                                = optional(string, "path/")
    region                              = optional(string, "us-east-1")
    s3-api-version                      = optional(string, "2")
    s3-uri-style                        = optional(string, "2")
    storage-class                       = optional(string, "")
    tls-ca-chain                        = optional(string, "")
  })
  default = {
  }
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
