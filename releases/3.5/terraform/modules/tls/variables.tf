# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model" {
  type     = string
  default  = "spark"
  nullable = false
}

variable "channel" {
  type    = string
  default = "latest/stable"
}

variable "app_name" {
  type     = string
  default  = "certificates"
  nullable = false
}
