# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Define cos-specific variables

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

variable "alertmanager_size" {
  description = "Storage size for the alertmanager database"
  type        = string
  default     = "10G"
}

variable "grafana_size" {
  description = "Storage size for the grafana database"
  type        = string
  default     = "10G"
}

variable "loki_active_index_directory_size" {
  description = "Storage size for the active index directory for Loki"
  type        = string
  default     = "10G"
}

variable "loki_chunks_size" {
  description = "Storage size for the Loki chucks storage"
  type        = string
  default     = "500G"
}

variable "prometheus_size" {
  description = "Storage size for the Prometheus database"
  type        = string
  default     = "500G"
}

variable "traefik_size" {
  description = "Storage size for the Traefik storage"
  type        = string
  default     = "10G"
}
