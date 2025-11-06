# ================================
# Resource Group
# ================================

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# ================================
# Random Suffix for Unique Names
# ================================

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# ================================
# Networking Module
# ================================

module "networking" {
  source = "./modules/networking"

  project_name              = var.project_name
  environment               = var.environment
  location                  = var.location
  resource_group_name       = azurerm_resource_group.main.name
  vnet_address_space        = var.vnet_address_space
  subnet_api_services       = var.subnet_api_services
  subnet_internal_services  = var.subnet_internal_services
  subnet_data_layer         = var.subnet_data_layer
  subnet_app_gateway        = var.subnet_app_gateway
  enable_ddos_protection    = var.enable_ddos_protection
  tags                      = var.tags
}

# ================================
# Security Module (Key Vault, NSGs, Managed Identities)
# ================================

module "security" {
  source = "./modules/security"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  random_suffix       = random_string.suffix.result
  vnet_id             = module.networking.vnet_id
  subnet_data_layer_id = module.networking.subnet_data_layer_id

  # Secrets to store in Key Vault
  mysql_admin_username = var.mysql_admin_username
  mysql_admin_password = var.mysql_admin_password

  tags = var.tags

  depends_on = [module.networking]
}

# ================================
# Database Module (MySQL, Redis)
# ================================

module "database" {
  source = "./modules/database"

  project_name                  = var.project_name
  environment                   = var.environment
  location                      = var.location
  resource_group_name           = azurerm_resource_group.main.name
  random_suffix                 = random_string.suffix.result

  # MySQL Configuration
  mysql_admin_username          = var.mysql_admin_username
  mysql_admin_password          = var.mysql_admin_password
  mysql_sku_name                = var.mysql_sku_name
  mysql_storage_size_gb         = var.mysql_storage_size_gb
  mysql_version                 = var.mysql_version
  mysql_backup_retention_days   = var.mysql_backup_retention_days
  mysql_high_availability_enabled = var.mysql_high_availability_enabled

  # Redis Configuration
  redis_sku_name    = var.redis_sku_name
  redis_capacity    = var.redis_capacity
  redis_family      = var.redis_family

  # Networking
  subnet_data_layer_id = module.networking.subnet_data_layer_id
  vnet_id              = module.networking.vnet_id

  tags = var.tags

  depends_on = [module.networking, module.security]
}

# ================================
# Messaging Module (Service Bus)
# ================================

module "messaging" {
  source = "./modules/messaging"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  servicebus_sku      = var.servicebus_sku
  subnet_data_layer_id = module.networking.subnet_data_layer_id
  vnet_id             = module.networking.vnet_id

  tags = var.tags

  depends_on = [module.networking]
}

# ================================
# Email Module (Azure Communication Services / SendGrid / Custom SMTP)
# ================================

module "email" {
  source = "./modules/email"

  project_name                     = var.project_name
  environment                      = var.environment
  location                         = var.location
  resource_group_name              = azurerm_resource_group.main.name
  key_vault_id                     = module.security.key_vault_id
  subnet_internal_services_id      = module.networking.subnet_internal_services_id

  # Email Service Configuration (choose one)
  use_azure_communication_services = var.use_azure_communication_services
  email_domain                     = var.email_domain

  use_sendgrid                     = var.use_sendgrid
  sendgrid_api_key                 = var.sendgrid_api_key
  sendgrid_from_email              = var.sendgrid_from_email

  use_custom_smtp                  = var.use_custom_smtp
  smtp_host                        = var.smtp_host
  smtp_port                        = var.smtp_port
  smtp_username                    = var.smtp_username
  smtp_password                    = var.smtp_password
  smtp_from_email                  = var.smtp_from_email
  smtp_use_tls                     = var.smtp_use_tls

  # Development: MailHog
  deploy_mailhog_dev               = var.deploy_mailhog_dev

  tags = var.tags

  depends_on = [module.networking, module.security]
}

# ================================
# Container Registry Module
# ================================

resource "azurerm_container_registry" "acr" {
  name                = "${var.project_name}acr${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = var.acr_sku
  admin_enabled       = true

  tags = var.tags
}

# ================================
# Monitoring Module (Application Insights, Log Analytics)
# ================================

module "monitoring" {
  source = "./modules/monitoring"

  project_name               = var.project_name
  environment                = var.environment
  location                   = var.location
  resource_group_name        = azurerm_resource_group.main.name
  log_retention_days         = var.log_retention_days
  enable_application_insights = var.enable_application_insights

  tags = var.tags
}

# ================================
# Compute Module (AKS or Container Apps)
# ================================

module "compute" {
  source = "./modules/compute"

  project_name        = var.project_name
  environment         = var.environment
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name

  # Networking
  subnet_api_services_id      = module.networking.subnet_api_services_id
  subnet_internal_services_id = module.networking.subnet_internal_services_id

  # AKS Configuration
  use_aks           = var.use_aks
  aks_node_count    = var.aks_node_count
  aks_node_vm_size  = var.aks_node_vm_size
  aks_min_count     = var.aks_min_count
  aks_max_count     = var.aks_max_count

  # Container Registry
  acr_id            = azurerm_container_registry.acr.id
  acr_login_server  = azurerm_container_registry.acr.login_server

  # Monitoring
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  application_insights_key   = module.monitoring.application_insights_instrumentation_key

  # Service Configuration
  service_replicas  = var.service_replicas
  docker_images     = var.docker_images

  # Database Connection Strings (from Key Vault)
  mysql_connection_string = module.database.mysql_connection_string
  redis_connection_string = module.database.redis_connection_string
  servicebus_connection_string = module.messaging.servicebus_connection_string

  # Ollama Configuration
  ollama_vm_size = var.ollama_vm_size
  ollama_model   = var.ollama_model

  # Security
  key_vault_id = module.security.key_vault_id
  managed_identity_ids = module.security.managed_identity_ids

  tags = var.tags

  depends_on = [
    module.networking,
    module.database,
    module.messaging,
    module.security,
    module.monitoring
  ]
}

# ================================
# Application Gateway (Public Entry Point)
# ================================

# Public IP for Application Gateway
resource "azurerm_public_ip" "app_gateway" {
  name                = "${var.project_name}-${var.environment}-agw-pip"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

# Application Gateway with WAF
resource "azurerm_application_gateway" "main" {
  name                = "${var.project_name}-${var.environment}-agw"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location

  sku {
    name     = var.app_gateway_sku
    tier     = var.app_gateway_sku
    capacity = var.app_gateway_capacity
  }

  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = module.networking.subnet_app_gateway_id
  }

  frontend_port {
    name = "https-port"
    port = 443
  }

  frontend_port {
    name = "http-port"
    port = 80
  }

  frontend_ip_configuration {
    name                 = "frontend-ip-config"
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }

  # Backend pools for each service
  backend_address_pool {
    name = "identity-service-pool"
    # fqdns will be populated from Container Apps or AKS service endpoints
  }

  backend_address_pool {
    name = "upload-service-pool"
  }

  backend_address_pool {
    name = "data-service-pool"
  }

  # HTTP Settings
  backend_http_settings {
    name                  = "http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
    probe_name            = "health-probe"
  }

  # Health Probe
  probe {
    name                = "health-probe"
    protocol            = "Http"
    path                = "/health"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
    host                = "127.0.0.1"
  }

  # HTTP Listener (redirect to HTTPS)
  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "frontend-ip-config"
    frontend_port_name             = "http-port"
    protocol                       = "Http"
  }

  # HTTPS Listener (TODO: Configure SSL certificate)
  # Uncomment and configure when SSL certificate is available
  # http_listener {
  #   name                           = "https-listener"
  #   frontend_ip_configuration_name = "frontend-ip-config"
  #   frontend_port_name             = "https-port"
  #   protocol                       = "Https"
  #   ssl_certificate_name           = "flowlite-ssl-cert"
  # }

  # Request routing rule (HTTP)
  request_routing_rule {
    name                       = "http-routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "identity-service-pool"
    backend_http_settings_name = "http-settings"
    priority                   = 100
  }

  # WAF Configuration
  dynamic "waf_configuration" {
    for_each = var.enable_waf ? [1] : []
    content {
      enabled          = true
      firewall_mode    = "Prevention"
      rule_set_type    = "OWASP"
      rule_set_version = "3.2"
    }
  }

  tags = var.tags

  depends_on = [module.compute]
}

# ================================
# Key Vault Secrets for Connection Strings
# ================================

resource "azurerm_key_vault_secret" "mysql_connection_string" {
  name         = "mysql-connection-string"
  value        = module.database.mysql_connection_string
  key_vault_id = module.security.key_vault_id

  depends_on = [module.security]
}

resource "azurerm_key_vault_secret" "redis_connection_string" {
  name         = "redis-connection-string"
  value        = module.database.redis_connection_string
  key_vault_id = module.security.key_vault_id

  depends_on = [module.security]
}

resource "azurerm_key_vault_secret" "servicebus_connection_string" {
  name         = "servicebus-connection-string"
  value        = module.messaging.servicebus_connection_string
  key_vault_id = module.security.key_vault_id

  depends_on = [module.security]
}

resource "azurerm_key_vault_secret" "acr_admin_password" {
  name         = "acr-admin-password"
  value        = azurerm_container_registry.acr.admin_password
  key_vault_id = module.security.key_vault_id

  depends_on = [module.security]
}
