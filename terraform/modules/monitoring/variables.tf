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

variable "log_retention_days" {
  description = "Log retention in days"
  type        = number
}

variable "enable_application_insights" {
  description = "Enable Application Insights"
  type        = bool
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
