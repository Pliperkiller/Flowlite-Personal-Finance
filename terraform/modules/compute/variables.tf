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

variable "subnet_api_services_id" {
  description = "API services subnet ID"
  type        = string
}

variable "subnet_internal_services_id" {
  description = "Internal services subnet ID"
  type        = string
}

variable "use_aks" {
  description = "Use Azure Kubernetes Service"
  type        = bool
}

variable "aks_node_count" {
  description = "AKS initial node count"
  type        = number
}

variable "aks_node_vm_size" {
  description = "AKS node VM size"
  type        = string
}

variable "aks_min_count" {
  description = "AKS minimum node count"
  type        = number
}

variable "aks_max_count" {
  description = "AKS maximum node count"
  type        = number
}

variable "acr_id" {
  description = "Azure Container Registry ID"
  type        = string
}

variable "acr_login_server" {
  description = "Azure Container Registry login server"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  type        = string
}

variable "application_insights_key" {
  description = "Application Insights instrumentation key"
  type        = string
  sensitive   = true
}

variable "service_replicas" {
  description = "Service replica counts"
  type = object({
    identity_service = number
    upload_service   = number
    data_service     = number
    insight_service  = number
  })
}

variable "docker_images" {
  description = "Docker image tags"
  type = object({
    identity_service = string
    upload_service   = string
    data_service     = string
    insight_service  = string
  })
}

variable "mysql_connection_string" {
  description = "MySQL connection string"
  type        = string
  sensitive   = true
}

variable "redis_connection_string" {
  description = "Redis connection string"
  type        = string
  sensitive   = true
}

variable "servicebus_connection_string" {
  description = "Service Bus connection string"
  type        = string
  sensitive   = true
}

variable "ollama_vm_size" {
  description = "Ollama VM size"
  type        = string
}

variable "ollama_model" {
  description = "Ollama model name"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID"
  type        = string
}

variable "managed_identity_ids" {
  description = "Managed Identity IDs"
  type        = map(string)
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
