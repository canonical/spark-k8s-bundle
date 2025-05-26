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

variable "AZURE_RESOURCE_GROUP" {
  type = string
  description = "Name of the resource group to be created for the Azure Blob storage"
  default = "TestSparkAKS"
}

variable "AZURE_REGION" {
  type = string
  description = "Location to be used for Azure Blob Storage deployment"
  default = "East US"
}

variable "AZURE_STORAGE_ACCOUNT" {
  type = string
  description = "Name for the storage account to be used for the Azure Blob Storage"
  default = "sparktestaks"
}
