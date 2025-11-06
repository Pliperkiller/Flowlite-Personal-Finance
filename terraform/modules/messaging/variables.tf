variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "servicebus_sku" {
  description = "Service Bus SKU (Basic, Standard, Premium)"
  type        = string
}

variable "subnet_data_layer_id" {
  description = "Data layer subnet ID for private endpoint"
  type        = string
}

variable "vnet_id" {
  description = "Virtual Network ID"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
