# ================================
# Virtual Network
# ================================

resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-${var.environment}-vnet"
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = var.vnet_address_space

  tags = var.tags
}

# ================================
# Subnets
# ================================

# Subnet for API Services (IdentityService, UploadService, DataService)
resource "azurerm_subnet" "api_services" {
  name                 = "${var.project_name}-${var.environment}-api-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_api_services]

  # Service endpoints for accessing Azure services
  service_endpoints = [
    "Microsoft.Sql",
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.ServiceBus"
  ]

  delegation {
    name = "container-apps-delegation"
    service_delegation {
      name    = "Microsoft.App/environments"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

# Subnet for Internal Services (InsightService, Ollama)
resource "azurerm_subnet" "internal_services" {
  name                 = "${var.project_name}-${var.environment}-internal-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_internal_services]

  service_endpoints = [
    "Microsoft.Sql",
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.ServiceBus"
  ]
}

# Subnet for Data Layer (MySQL, Redis, Service Bus Private Endpoints)
resource "azurerm_subnet" "data_layer" {
  name                 = "${var.project_name}-${var.environment}-data-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_data_layer]

  service_endpoints = [
    "Microsoft.Sql",
    "Microsoft.Storage"
  ]

  # Enable private endpoint network policies
  private_endpoint_network_policies_enabled = false
}

# Subnet for Application Gateway
resource "azurerm_subnet" "app_gateway" {
  name                 = "${var.project_name}-${var.environment}-agw-subnet"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_app_gateway]
}

# ================================
# Network Security Groups
# ================================

# NSG for API Services Subnet
resource "azurerm_network_security_group" "api_services" {
  name                = "${var.project_name}-${var.environment}-api-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name

  # Allow HTTPS from Application Gateway
  security_rule {
    name                       = "AllowHTTPSFromAppGateway"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = var.subnet_app_gateway
    destination_address_prefix = "*"
  }

  # Allow HTTP from Application Gateway (internal)
  security_rule {
    name                       = "AllowHTTPFromAppGateway"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["8000", "8001", "8003"]
    source_address_prefix      = var.subnet_app_gateway
    destination_address_prefix = "*"
  }

  # Allow internal service-to-service communication
  security_rule {
    name                       = "AllowInternalServices"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["8000", "8001", "8003"]
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Deny all other inbound traffic
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# NSG for Internal Services Subnet
resource "azurerm_network_security_group" "internal_services" {
  name                = "${var.project_name}-${var.environment}-internal-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name

  # Allow traffic only from within VNet
  security_rule {
    name                       = "AllowVNetInbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["8002", "11434"]
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Deny all other inbound traffic
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# NSG for Data Layer Subnet
resource "azurerm_network_security_group" "data_layer" {
  name                = "${var.project_name}-${var.environment}-data-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name

  # Allow MySQL from VNet
  security_rule {
    name                       = "AllowMySQL"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3306"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Allow Redis from VNet
  security_rule {
    name                       = "AllowRedis"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "6379"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Allow Service Bus from VNet
  security_rule {
    name                       = "AllowServiceBus"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["5671", "5672"]
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "*"
  }

  # Deny all other inbound traffic
  security_rule {
    name                       = "DenyAllInbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = var.tags
}

# ================================
# NSG Associations
# ================================

resource "azurerm_subnet_network_security_group_association" "api_services" {
  subnet_id                 = azurerm_subnet.api_services.id
  network_security_group_id = azurerm_network_security_group.api_services.id
}

resource "azurerm_subnet_network_security_group_association" "internal_services" {
  subnet_id                 = azurerm_subnet.internal_services.id
  network_security_group_id = azurerm_network_security_group.internal_services.id
}

resource "azurerm_subnet_network_security_group_association" "data_layer" {
  subnet_id                 = azurerm_subnet.data_layer.id
  network_security_group_id = azurerm_network_security_group.data_layer.id
}

# ================================
# NAT Gateway for Outbound Internet Access
# ================================

resource "azurerm_public_ip" "nat_gateway" {
  name                = "${var.project_name}-${var.environment}-nat-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

resource "azurerm_nat_gateway" "main" {
  name                = "${var.project_name}-${var.environment}-nat-gateway"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = "Standard"

  tags = var.tags
}

resource "azurerm_nat_gateway_public_ip_association" "main" {
  nat_gateway_id       = azurerm_nat_gateway.main.id
  public_ip_address_id = azurerm_public_ip.nat_gateway.id
}

# Associate NAT Gateway with internal services subnet
resource "azurerm_subnet_nat_gateway_association" "internal_services" {
  subnet_id      = azurerm_subnet.internal_services.id
  nat_gateway_id = azurerm_nat_gateway.main.id
}

# ================================
# DDoS Protection Plan (Optional - Expensive)
# ================================

resource "azurerm_network_ddos_protection_plan" "main" {
  count               = var.enable_ddos_protection ? 1 : 0
  name                = "${var.project_name}-${var.environment}-ddos-plan"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.tags
}
