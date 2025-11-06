# ================================
# General Variables
# ================================

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "flowlite"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Flowlite"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

# ================================
# Networking Variables
# ================================

variable "vnet_address_space" {
  description = "Address space for Virtual Network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_api_services" {
  description = "Subnet for API services (IdentityService, UploadService, DataService)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "subnet_internal_services" {
  description = "Subnet for internal services (InsightService, Ollama)"
  type        = string
  default     = "10.0.2.0/24"
}

variable "subnet_data_layer" {
  description = "Subnet for data layer (MySQL, Redis, Service Bus)"
  type        = string
  default     = "10.0.3.0/24"
}

variable "subnet_app_gateway" {
  description = "Subnet for Application Gateway"
  type        = string
  default     = "10.0.4.0/24"
}

# ================================
# Database Variables
# ================================

variable "mysql_admin_username" {
  description = "MySQL administrator username"
  type        = string
  default     = "flowliteadmin"
  sensitive   = true
}

variable "mysql_admin_password" {
  description = "MySQL administrator password"
  type        = string
  sensitive   = true
}

variable "mysql_sku_name" {
  description = "MySQL SKU name (B_Standard_B2s, GP_Standard_D2ds_v4, etc.)"
  type        = string
  default     = "B_Standard_B2s" # Burstable for dev/test
}

variable "mysql_storage_size_gb" {
  description = "MySQL storage size in GB"
  type        = number
  default     = 20
}

variable "mysql_version" {
  description = "MySQL version"
  type        = string
  default     = "8.0.21"
}

variable "mysql_backup_retention_days" {
  description = "MySQL backup retention in days"
  type        = number
  default     = 7
}

variable "mysql_high_availability_enabled" {
  description = "Enable MySQL high availability (zone redundant)"
  type        = bool
  default     = false # Set to true for production
}

# ================================
# Redis Variables
# ================================

variable "redis_sku_name" {
  description = "Redis SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"
}

variable "redis_capacity" {
  description = "Redis cache capacity (0-6 for Standard/Premium, 0-2 for Basic)"
  type        = number
  default     = 1 # C1: 1GB
}

variable "redis_family" {
  description = "Redis family (C for Basic/Standard, P for Premium)"
  type        = string
  default     = "C"
}

# ================================
# Service Bus Variables
# ================================

variable "servicebus_sku" {
  description = "Service Bus SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"
}

# ================================
# Container Registry Variables
# ================================

variable "acr_sku" {
  description = "Container Registry SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

# ================================
# Kubernetes / Container Apps Variables
# ================================

variable "use_aks" {
  description = "Use Azure Kubernetes Service (true) or Container Apps (false)"
  type        = bool
  default     = false # Container Apps is more cost-effective for microservices
}

variable "aks_node_count" {
  description = "Initial number of AKS nodes"
  type        = number
  default     = 2
}

variable "aks_node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "aks_min_count" {
  description = "Minimum number of AKS nodes for autoscaling"
  type        = number
  default     = 2
}

variable "aks_max_count" {
  description = "Maximum number of AKS nodes for autoscaling"
  type        = number
  default     = 10
}

# ================================
# Application Gateway Variables
# ================================

variable "app_gateway_sku" {
  description = "Application Gateway SKU"
  type        = string
  default     = "WAF_v2"
}

variable "app_gateway_capacity" {
  description = "Application Gateway capacity"
  type        = number
  default     = 2
}

variable "enable_waf" {
  description = "Enable Web Application Firewall"
  type        = bool
  default     = true
}

# ================================
# Ollama LLM Variables
# ================================

variable "ollama_vm_size" {
  description = "VM size for Ollama LLM (GPU required: Standard_NC6s_v3 or higher)"
  type        = string
  default     = "Standard_NC6s_v3" # 6 vCPU, 112 GB RAM, 1x V100 GPU
}

variable "ollama_model" {
  description = "Ollama model to use"
  type        = string
  default     = "llama3.1:8b"
}

# ================================
# Monitoring Variables
# ================================

variable "log_retention_days" {
  description = "Log Analytics retention in days"
  type        = number
  default     = 30
}

variable "enable_application_insights" {
  description = "Enable Application Insights"
  type        = bool
  default     = true
}

# ================================
# Security Variables
# ================================

variable "allowed_ip_ranges" {
  description = "Allowed IP ranges for management access"
  type        = list(string)
  default     = [] # Add your IPs here
}

variable "enable_ddos_protection" {
  description = "Enable DDoS Protection Standard"
  type        = bool
  default     = false # Expensive, enable for production
}

# ================================
# Service-specific Variables
# ================================

variable "service_replicas" {
  description = "Number of replicas for each service"
  type = object({
    identity_service = number
    upload_service   = number
    data_service     = number
    insight_service  = number
  })
  default = {
    identity_service = 2
    upload_service   = 2
    data_service     = 2
    insight_service  = 1
  }
}

variable "docker_images" {
  description = "Docker image tags for services"
  type = object({
    identity_service = string
    upload_service   = string
    data_service     = string
    insight_service  = string
  })
  default = {
    identity_service = "latest"
    upload_service   = "latest"
    data_service     = "latest"
    insight_service  = "latest"
  }
}

# ================================
# Cost Optimization Variables
# ================================

variable "auto_shutdown_time" {
  description = "Auto-shutdown time for dev/test VMs (HHmm format, e.g., 1900 for 7PM)"
  type        = string
  default     = "1900"
}

variable "enable_auto_shutdown" {
  description = "Enable auto-shutdown for dev/test resources"
  type        = bool
  default     = true
}
