
resource "azurerm_kubernetes_cluster" "prod-k8s" {
  location            = azurerm_resource_group.rg.location
  name                = var.cluster_name
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "testaksclusterprefix"
  kubernetes_version  = "1.31.7"

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name           = "default"
    vm_size        = "Standard_DS2_v2"
    node_count     = var.num_nodes
    vnet_subnet_id = azurerm_subnet.infrastructure.id
  }

  auto_scaler_profile {
    expander = "least-waste" # if not least waste
    #ignore-daemonsets-utilization = true
    scale_down_utilization_threshold = 0.2
    scale_down_unneeded              = "30m"
  }

  network_profile {
    network_plugin = "kubenet"
    service_cidr   = "10.1.0.0/16" # Ensure this does not overlap with any subnets
    dns_service_ip = "10.1.0.10"   # Hardcoded DNS service IP
  }
}
