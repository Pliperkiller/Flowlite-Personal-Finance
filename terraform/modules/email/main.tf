# ================================
# Email Service Module
# ================================
# This module provides email capabilities for the Flowlite application
# Options:
# 1. Azure Communication Services (Recommended for Azure)
# 2. SendGrid (Third-party, widely used)
# 3. Custom SMTP (For existing email infrastructure)
# ================================

# ================================
# Option 1: Azure Communication Services (Recommended)
# ================================

resource "azurerm_communication_service" "main" {
  count               = var.use_azure_communication_services ? 1 : 0
  name                = "${var.project_name}-${var.environment}-comm"
  resource_group_name = var.resource_group_name
  data_location       = "United States" # Options: "United States", "Europe", "Asia Pacific"

  tags = var.tags
}

# Email Communication Service (Preview)
resource "azurerm_email_communication_service" "main" {
  count               = var.use_azure_communication_services ? 1 : 0
  name                = "${var.project_name}-${var.environment}-email"
  resource_group_name = var.resource_group_name
  data_location       = "United States"

  tags = var.tags
}

# Email Domain (requires manual verification in Azure Portal)
resource "azurerm_email_communication_service_domain" "main" {
  count                    = var.use_azure_communication_services && var.email_domain != "" ? 1 : 0
  name                     = var.email_domain
  email_service_id         = azurerm_email_communication_service.main[0].id
  domain_management        = "CustomerManaged" # or "AzureManaged" for *.azurecomm.net

  tags = var.tags
}

# Store connection string in Key Vault
resource "azurerm_key_vault_secret" "acs_connection_string" {
  count        = var.use_azure_communication_services ? 1 : 0
  name         = "email-connection-string"
  value        = azurerm_communication_service.main[0].primary_connection_string
  key_vault_id = var.key_vault_id
}

# ================================
# Option 2: SendGrid (Third-party service)
# ================================

# SendGrid API Key (stored manually in Key Vault)
# You need to:
# 1. Create SendGrid account at https://sendgrid.com/
# 2. Generate API key
# 3. Store in Key Vault manually or via CI/CD

resource "azurerm_key_vault_secret" "sendgrid_api_key" {
  count        = var.use_sendgrid && var.sendgrid_api_key != "" ? 1 : 0
  name         = "sendgrid-api-key"
  value        = var.sendgrid_api_key
  key_vault_id = var.key_vault_id
}

# ================================
# Option 3: Custom SMTP Configuration
# ================================

resource "azurerm_key_vault_secret" "smtp_host" {
  count        = var.use_custom_smtp ? 1 : 0
  name         = "smtp-host"
  value        = var.smtp_host
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "smtp_port" {
  count        = var.use_custom_smtp ? 1 : 0
  name         = "smtp-port"
  value        = var.smtp_port
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "smtp_username" {
  count        = var.use_custom_smtp ? 1 : 0
  name         = "smtp-username"
  value        = var.smtp_username
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "smtp_password" {
  count        = var.use_custom_smtp ? 1 : 0
  name         = "smtp-password"
  value        = var.smtp_password
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "smtp_from_email" {
  count        = var.use_custom_smtp ? 1 : 0
  name         = "smtp-from-email"
  value        = var.smtp_from_email
  key_vault_id = var.key_vault_id
}

# ================================
# Development: MailHog Configuration
# ================================
# MailHog is ONLY for local development
# For Azure development environment, we use a simple SMTP relay

resource "azurerm_container_group" "mailhog" {
  count               = var.environment == "dev" && var.deploy_mailhog_dev ? 1 : 0
  name                = "${var.project_name}-mailhog-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  ip_address_type     = "Private"
  subnet_ids          = [var.subnet_internal_services_id]

  container {
    name   = "mailhog"
    image  = "mailhog/mailhog:latest"
    cpu    = "0.5"
    memory = "1.0"

    ports {
      port     = 1025
      protocol = "TCP"
    }

    ports {
      port     = 8025
      protocol = "TCP"
    }
  }

  tags = var.tags
}

# Store MailHog SMTP configuration for dev environment
resource "azurerm_key_vault_secret" "mailhog_smtp_host" {
  count        = var.environment == "dev" && var.deploy_mailhog_dev ? 1 : 0
  name         = "smtp-host"
  value        = azurerm_container_group.mailhog[0].ip_address
  key_vault_id = var.key_vault_id
}

resource "azurerm_key_vault_secret" "mailhog_smtp_port" {
  count        = var.environment == "dev" && var.deploy_mailhog_dev ? 1 : 0
  name         = "smtp-port"
  value        = "1025"
  key_vault_id = var.key_vault_id
}
