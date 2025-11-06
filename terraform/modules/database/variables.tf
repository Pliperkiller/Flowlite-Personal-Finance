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

variable "random_suffix" {
  description = "Random suffix for unique names"
  type        = string
}

variable "mysql_admin_username" {
  description = "MySQL admin username"
  type        = string
  sensitive   = true
}

variable "mysql_admin_password" {
  description = "MySQL admin password"
  type        = string
  sensitive   = true
}

variable "mysql_sku_name" {
  description = "MySQL SKU name"
  type        = string
}

variable "mysql_storage_size_gb" {
  description = "MySQL storage size in GB"
  type        = number
}

variable "mysql_version" {
  description = "MySQL version"
  type        = string
}

variable "mysql_backup_retention_days" {
  description = "MySQL backup retention days"
  type        = number
}

variable "mysql_high_availability_enabled" {
  description = "Enable MySQL high availability"
  type        = bool
}

variable "redis_sku_name" {
  description = "Redis SKU name"
  type        = string
}

variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
}

variable "redis_family" {
  description = "Redis family"
  type        = string
}

variable "subnet_data_layer_id" {
  description = "Data layer subnet ID"
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
