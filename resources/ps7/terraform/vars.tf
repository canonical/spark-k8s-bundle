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

variable "S3_ENDPOINT_URL" {
  type        = string
  description = "S3 endpoint"
}

variable "S3_ACCESS_KEY" {
  type        = string
  description = "S3 access key"
}

variable "S3_SECRET_KEY" {
  type        = string
  description = "S3 secret key"
}

variable "HTTP_PROXY" {
  description = "Value of the http_proxy environment variable"
  type        = string
  default     = ""
}

variable "HTTPS_PROXY" {
  description = "Value of the https_proxy environment variable"
  type        = string
  default     = ""
}

variable "NO_PROXY" {
  description = "Value of the no_proxy environment variable"
  type        = string
  default     = ""
}