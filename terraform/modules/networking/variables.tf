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

variable "vnet_address_space" {
  description = "Virtual Network address space"
  type        = list(string)
}

variable "subnet_api_services" {
  description = "API services subnet CIDR"
  type        = string
}

variable "subnet_internal_services" {
  description = "Internal services subnet CIDR"
  type        = string
}

variable "subnet_data_layer" {
  description = "Data layer subnet CIDR"
  type        = string
}

variable "subnet_app_gateway" {
  description = "Application Gateway subnet CIDR"
  type        = string
}

variable "enable_ddos_protection" {
  description = "Enable DDoS Protection"
  type        = bool
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
