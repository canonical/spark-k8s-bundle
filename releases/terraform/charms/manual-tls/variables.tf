# Variables for $(basename "$moduleDir").

variable "app_name" {
  description = "Name to give the deployed application."
  type        = string
  default     = "certificates"
}

variable "channel" {
  description = "Channel for the charm."
  type        = string
  default     = "latest/stable"
}

variable "config" {
  description = "Application config for the charm."
  type        = map(string)
  default     = {}
}

variable "constraints" {
  description = "Juju constraints for the charm deployment."
  type        = string
  default     = "arch=amd64"
}

variable "model" {
  description = "Target Juju model name (fallback if model_uuid is not provided)."
  type        = string
  default     = "spark"
}

variable "model_uuid" {
  description = "Optional existing Juju model UUID to deploy the charm into."
  type        = string
  default     = null
}

variable "revision" {
  description = "Charm revision number (null means latest)."
  type        = number
  default     = null
}

variable "units" {
  description = "Number of units for the application."
  type        = number
  default     = 1
}

