variable "model" {
  description = "The name of the Juju model to deploy to"
  type        = string
}

variable "spark_model" {
  description = "The name of the Juju model where spark is deployed."
  type        = string
}


variable "identity_user" {
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

variable "spark_charms" {
  description = "The names of the Spark applications in the Spark Juju model."
  type        = map(string)
}

# variable "identity_charms" {
#   description = "The names of the Identity applications in the identity Juju model."
#   type        = map(string)
# }
