# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define cos-specific variables

variable "K8S_CLOUD" {
  type        = string
  description = "The kubernetes juju cloud name."
}

variable "K8S_CREDENTIAL" {
  type        = string
  description = "The name of the kubernetes juju credential."
}

variable "model" {
  description = "The name of the Juju model to deploy to"
  type        = string
}

variable "cos_user" {
  description = "The name of the Juju user of the COS deployment."
  type        = string
  default     = "admin"
}

variable "cos_tls_cert" {
  type        = string
  default     = ""
  description = "COS certificate"
}

variable "cos_tls_key" {
  type        = string
  default     = ""
  description = "COS certificate key"
}

variable "cos_tls_ca" {
  type        = string
  default     = ""
  description = "COS CA certificate"
}

