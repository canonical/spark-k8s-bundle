
output "resource_group_name" {
  value = azurerm_resource_group.rg.name
  description = "The name of the resource group"
}


output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.prod-k8s.name
  description = "The name of the AKS cluster"
}

