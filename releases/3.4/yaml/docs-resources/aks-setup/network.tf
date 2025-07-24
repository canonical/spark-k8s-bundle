resource "azurerm_virtual_network" "vn" {
  name                = "TestSparkAKSVN"
  address_space       = ["10.0.0.0/16"]  # Define the address space for the VNet
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}


resource "azurerm_subnet" "infrastructure" {
  name                 = "testsparkaks-subnet"
  virtual_network_name = azurerm_virtual_network.vn.name
  resource_group_name  = azurerm_resource_group.rg.name
  address_prefixes     = ["10.0.10.0/24"]
}


resource "azurerm_nat_gateway" "natgw" {
  location            = azurerm_resource_group.rg.location
  name                = "testsparkaks-nat-gateway"
  resource_group_name = azurerm_resource_group.rg.name
  sku_name                = "Standard"

}


resource "azurerm_public_ip" "natip" {
  name                = "testsparkaks-nat-gateway-ip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}


resource "azurerm_nat_gateway_public_ip_association" "example" {
  nat_gateway_id       = azurerm_nat_gateway.natgw.id
  public_ip_address_id = azurerm_public_ip.natip.id
}


resource "azurerm_subnet_nat_gateway_association" "natinfra" {
  subnet_id      = azurerm_subnet.infrastructure.id
  nat_gateway_id = azurerm_nat_gateway.natgw.id
}


resource "azurerm_network_security_group" "infra_sec_group" {
  name                = "TestAKSInfrastructureSecurityGroup"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "AllowAnyCustomAnyOutbound"
    priority                   = 110
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowNATInbound"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = azurerm_public_ip.natip.ip_address
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow80AnyInbound"
    priority                   = 130
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow443AnyInbound"
    priority                   = 140
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow8080AnyInbound"
    priority                   = 150
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}


resource "azurerm_subnet_network_security_group_association" "infra-association" {
  subnet_id                 = azurerm_subnet.infrastructure.id
  network_security_group_id = azurerm_network_security_group.infra_sec_group.id
}
