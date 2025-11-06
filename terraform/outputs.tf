# ================================
# General Outputs
# ================================

output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "location" {
  description = "Azure region"
  value       = var.location
}

# ================================
# Networking Outputs
# ================================

output "vnet_id" {
  description = "Virtual Network ID"
  value       = module.networking.vnet_id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = module.networking.vnet_name
}

output "subnet_api_services_id" {
  description = "API Services subnet ID"
  value       = module.networking.subnet_api_services_id
}

output "subnet_internal_services_id" {
  description = "Internal Services subnet ID"
  value       = module.networking.subnet_internal_services_id
}

output "subnet_data_layer_id" {
  description = "Data Layer subnet ID"
  value       = module.networking.subnet_data_layer_id
}

# ================================
# Database Outputs
# ================================

output "mysql_server_name" {
  description = "MySQL server name"
  value       = module.database.mysql_server_name
}

output "mysql_fqdn" {
  description = "MySQL fully qualified domain name"
  value       = module.database.mysql_fqdn
  sensitive   = true
}

output "redis_hostname" {
  description = "Redis cache hostname"
  value       = module.database.redis_hostname
  sensitive   = true
}

output "redis_port" {
  description = "Redis cache port"
  value       = module.database.redis_port
}

# ================================
# Messaging Outputs
# ================================

output "servicebus_namespace" {
  description = "Service Bus namespace name"
  value       = module.messaging.servicebus_namespace
}

output "servicebus_queue_name" {
  description = "Service Bus queue name for batch processing"
  value       = module.messaging.servicebus_queue_name
}

# ================================
# Container Registry Outputs
# ================================

output "acr_name" {
  description = "Azure Container Registry name"
  value       = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "Azure Container Registry admin username"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

# ================================
# Security Outputs
# ================================

output "key_vault_name" {
  description = "Key Vault name"
  value       = module.security.key_vault_name
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = module.security.key_vault_uri
}

output "managed_identity_ids" {
  description = "Managed Identity IDs for services"
  value       = module.security.managed_identity_ids
}

# ================================
# Monitoring Outputs
# ================================

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = module.monitoring.log_analytics_workspace_id
}

output "application_insights_instrumentation_key" {
  description = "Application Insights Instrumentation Key"
  value       = module.monitoring.application_insights_instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Application Insights Connection String"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}

# ================================
# Email Service Outputs
# ================================

output "email_service_type" {
  description = "Type of email service deployed"
  value       = module.email.email_service_type
}

output "mailhog_web_ui" {
  description = "MailHog Web UI URL (dev only)"
  value       = module.email.mailhog_web_ui
}

output "mailhog_smtp_config" {
  description = "MailHog SMTP configuration (dev only)"
  value = var.deploy_mailhog_dev && var.environment == "dev" ? {
    host = module.email.mailhog_smtp_host
    port = module.email.mailhog_smtp_port
  } : null
}

# ================================
# Compute Outputs
# ================================

output "aks_cluster_name" {
  description = "AKS cluster name (if using AKS)"
  value       = var.use_aks ? module.compute.aks_cluster_name : null
}

output "aks_cluster_fqdn" {
  description = "AKS cluster FQDN (if using AKS)"
  value       = var.use_aks ? module.compute.aks_cluster_fqdn : null
}

output "container_app_environment_name" {
  description = "Container Apps Environment name (if using Container Apps)"
  value       = !var.use_aks ? module.compute.container_app_environment_name : null
}

output "service_endpoints" {
  description = "Service endpoints"
  value       = module.compute.service_endpoints
  sensitive   = true
}

# ================================
# Application Gateway Outputs
# ================================

output "app_gateway_public_ip" {
  description = "Application Gateway public IP address"
  value       = azurerm_public_ip.app_gateway.ip_address
}

output "app_gateway_fqdn" {
  description = "Application Gateway FQDN"
  value       = azurerm_public_ip.app_gateway.fqdn
}

# ================================
# Connection Instructions
# ================================

output "connection_instructions" {
  description = "Instructions for connecting to services"
  value = <<-EOT
    ===================================================
    Flowlite Azure Infrastructure - Connection Details
    ===================================================

    1. CONTAINER REGISTRY
       Login Server: ${azurerm_container_registry.acr.login_server}
       Username: ${azurerm_container_registry.acr.admin_username}

       Login command:
       az acr login --name ${azurerm_container_registry.acr.name}

    2. DATABASE (MySQL)
       Server: ${module.database.mysql_fqdn}
       Database: flowlite_db
       Username: ${var.mysql_admin_username}

       Connection string stored in Key Vault:
       az keyvault secret show --vault-name ${module.security.key_vault_name} --name mysql-connection-string

    3. REDIS CACHE
       Hostname: ${module.database.redis_hostname}
       Port: ${module.database.redis_port}

       Connection string stored in Key Vault:
       az keyvault secret show --vault-name ${module.security.key_vault_name} --name redis-connection-string

    4. SERVICE BUS
       Namespace: ${module.messaging.servicebus_namespace}
       Queue: ${module.messaging.servicebus_queue_name}

       Connection string stored in Key Vault:
       az keyvault secret show --vault-name ${module.security.key_vault_name} --name servicebus-connection-string

    5. APPLICATION GATEWAY
       Public IP: ${azurerm_public_ip.app_gateway.ip_address}
       Access your services through: http://${azurerm_public_ip.app_gateway.ip_address}

    6. MONITORING
       Application Insights: ${module.monitoring.application_insights_name}
       Log Analytics: ${module.monitoring.log_analytics_workspace_name}

    7. KEY VAULT
       Vault Name: ${module.security.key_vault_name}
       URI: ${module.security.key_vault_uri}

    ===================================================
    Next Steps:
    ===================================================
    1. Build and push Docker images to ACR
    2. Configure Application Gateway backend pools with service FQDNs
    3. Set up CI/CD pipeline (GitHub Actions or Azure DevOps)
    4. Configure DNS records for custom domain
    5. Upload SSL certificate to Key Vault and configure in App Gateway
    6. Run database migrations
    7. Configure monitoring alerts

    For detailed instructions, see: docs/AZURE_ARCHITECTURE.md
    ===================================================
  EOT
}

# ================================
# Cost Estimation
# ================================

output "estimated_monthly_cost" {
  description = "Estimated monthly cost in USD (approximate)"
  value = <<-EOT
    Estimated Monthly Cost (${var.environment} environment):
    - Application Gateway WAF v2: $250
    - ${var.use_aks ? "AKS Cluster" : "Container Apps"}: ${var.use_aks ? "$280" : "$100"}
    - Azure MySQL ${var.mysql_sku_name}: ${var.mysql_sku_name == "B_Standard_B2s" ? "$85" : "$200+"}
    - Azure Redis ${var.redis_sku_name} ${var.redis_family}${var.redis_capacity}: ${var.redis_sku_name == "Standard" ? "$15-50" : "$170+"}
    - Azure Service Bus ${var.servicebus_sku}: ${var.servicebus_sku == "Standard" ? "$10" : "$670"}
    - Container Registry: $5
    - Key Vault: $5
    - Application Insights: $50
    - Storage Account: $20
    - Ollama VM (${var.ollama_vm_size}): $900

    TOTAL: ~$${var.use_aks ? "1,600" : "1,420"} - $2,500/month

    Note: Costs vary by region, actual usage, and data transfer.
    Consider Reserved Instances for 30-50% savings on VMs and databases.
  EOT
}
