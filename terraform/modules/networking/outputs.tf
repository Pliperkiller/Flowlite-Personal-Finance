output "vnet_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.main.id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = azurerm_virtual_network.main.name
}

output "subnet_api_services_id" {
  description = "API Services subnet ID"
  value       = azurerm_subnet.api_services.id
}

output "subnet_internal_services_id" {
  description = "Internal Services subnet ID"
  value       = azurerm_subnet.internal_services.id
}

output "subnet_data_layer_id" {
  description = "Data Layer subnet ID"
  value       = azurerm_subnet.data_layer.id
}

output "subnet_app_gateway_id" {
  description = "Application Gateway subnet ID"
  value       = azurerm_subnet.app_gateway.id
}

output "nsg_api_services_id" {
  description = "API Services NSG ID"
  value       = azurerm_network_security_group.api_services.id
}

output "nsg_internal_services_id" {
  description = "Internal Services NSG ID"
  value       = azurerm_network_security_group.internal_services.id
}

output "nsg_data_layer_id" {
  description = "Data Layer NSG ID"
  value       = azurerm_network_security_group.data_layer.id
}

output "nat_gateway_public_ip" {
  description = "NAT Gateway public IP"
  value       = azurerm_public_ip.nat_gateway.ip_address
}
