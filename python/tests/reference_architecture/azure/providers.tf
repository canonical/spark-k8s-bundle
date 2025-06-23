terraform {
  required_version = ">=1.0"

  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~>1.5"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.9.1"
    }
	juju = {
      source  = "juju/juju"
  	  version = ">=0.16.0,<0.20.0"
	}

  }
}

provider "juju" {
  controller_addresses = var.JUJU_CONTROLLER_IPS
  username         	= var.JUJU_USERNAME
  password         	= var.JUJU_PASSWORD
  ca_certificate   	= base64decode(var.JUJU_CA_CERTIFICATE)
}

provider "azurerm" {
  features {}
}