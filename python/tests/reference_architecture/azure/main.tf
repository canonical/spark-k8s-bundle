resource "azurerm_resource_group" "rg" {
  name     = var.AZURE_RESOURCE_GROUP
  location = var.AZURE_REGION
}

resource "azurerm_storage_account" "storageaccount" {
  name                     = var.AZURE_STORAGE_ACCOUNT
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = "true"
}


resource "azurerm_storage_container" "storagecontainer" {
  name                  = "sparktestcontainer"
  storage_account_name  = azurerm_storage_account.storageaccount.name
  container_access_type = "private"
}


resource "azurerm_storage_blob" "spark-folder" {
  name                   = "spark-events/example.txt"
  storage_account_name   = azurerm_storage_account.storageaccount.name
  storage_container_name = azurerm_storage_container.storagecontainer.name
  type                   = "Block"
  source                 = "./../../integration/resources/example.txt"
}

# Add COS

resource "juju_model" "cos" {
  name       = "cos"
  credential = var.K8S_CREDENTIAL
  cloud {
    name = var.K8S_CLOUD
  }
}

module "cos" {
  depends_on = [juju_model.cos]
  source     = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.4/terraform/external/cos"
  model      = juju_model.cos.name
}


module "spark" {
  source                	= "git::https://github.com/canonical/spark-k8s-bundle//releases/3.4/terraform"
  # source                	= "../../../../releases/3.4/terraform"
  model                 	= "spark"
  create_model              = true
  K8S_CLOUD                 = var.K8S_CLOUD
  K8S_CREDENTIAL            = var.K8S_CREDENTIAL
  storage_backend           = "azure_storage"
  azure_storage             = {
    container       = azurerm_storage_container.storagecontainer.name
    storage_account = azurerm_storage_account.storageaccount.name
    secret_key      = azurerm_storage_account.storageaccount.primary_access_key
    protocol        = "abfss"
  }
  cos = {
    deployed = "external"
    offers={
      dashboard=module.cos.dashboards_offer,
      metrics=module.cos.metrics_offer,
      logging=module.cos.logging_offer
    }
  }
}
