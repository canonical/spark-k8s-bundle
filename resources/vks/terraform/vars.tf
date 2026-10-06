variable "JUJU_CONTROLLER_IPS" {
  type        = string
  description = "Juju controller IP addresses, comma separated"
}

variable "JUJU_USERNAME" {
  type        = string
  description = "Username for the juju controller"
}

variable "JUJU_PASSWORD" {
  type        = string
  description = "Password for the juju controller"
}

variable "JUJU_CA_CERTIFICATE" {
  type        = string
  description = "Juju controller CA certificate"
}

variable "K8S_CLOUD" {
  type        = string
  description = "The kubernetes juju cloud name."
}

variable "K8S_CREDENTIAL" {
  type        = string
  description = "The name of the kubernetes juju credential."
}

variable "S3_ACCESS_KEY" {
  type        = string
  description = "S3 access key"
}

variable "S3_SECRET_KEY" {
  type        = string
  description = "S3 secret key"
}