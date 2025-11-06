# ================================
# Data Source - Current Client
# ================================

data "azurerm_client_config" "current" {}

# ================================
# Key Vault
# ================================

resource "azurerm_key_vault" "main" {
  name                       = "${var.project_name}kv${var.random_suffix}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false # Set to true for production

  # Enable access from VNet
  network_acls {
    bypass                     = "AzureServices"
    default_action             = "Deny"
    virtual_network_subnet_ids = [var.subnet_data_layer_id]
  }

  tags = var.tags
}

# Grant access to current user/service principal
resource "azurerm_key_vault_access_policy" "terraform" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Purge", "Recover"
  ]

  certificate_permissions = [
    "Get", "List", "Create", "Delete", "Purge"
  ]

  key_permissions = [
    "Get", "List", "Create", "Delete", "Purge"
  ]
}

# ================================
# Managed Identities for Services
# ================================

# Identity Service Managed Identity
resource "azurerm_user_assigned_identity" "identity_service" {
  name                = "${var.project_name}-${var.environment}-identity-mi"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.tags
}

# Upload Service Managed Identity
resource "azurerm_user_assigned_identity" "upload_service" {
  name                = "${var.project_name}-${var.environment}-upload-mi"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.tags
}

# Data Service Managed Identity
resource "azurerm_user_assigned_identity" "data_service" {
  name                = "${var.project_name}-${var.environment}-data-mi"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.tags
}

# Insight Service Managed Identity
resource "azurerm_user_assigned_identity" "insight_service" {
  name                = "${var.project_name}-${var.environment}-insight-mi"
  location            = var.location
  resource_group_name = var.resource_group_name

  tags = var.tags
}

# ================================
# Key Vault Access Policies for Managed Identities
# ================================

resource "azurerm_key_vault_access_policy" "identity_service" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.identity_service.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

resource "azurerm_key_vault_access_policy" "upload_service" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.upload_service.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

resource "azurerm_key_vault_access_policy" "data_service" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.data_service.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

resource "azurerm_key_vault_access_policy" "insight_service" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_user_assigned_identity.insight_service.principal_id

  secret_permissions = [
    "Get", "List"
  ]
}

# ================================
# Store Secrets in Key Vault
# ================================

resource "azurerm_key_vault_secret" "mysql_admin_username" {
  name         = "mysql-admin-username"
  value        = var.mysql_admin_username
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.terraform]
}

resource "azurerm_key_vault_secret" "mysql_admin_password" {
  name         = "mysql-admin-password"
  value        = var.mysql_admin_password
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.terraform]
}

# Generate random JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "azurerm_key_vault_secret" "jwt_secret" {
  name         = "jwt-secret-key"
  value        = random_password.jwt_secret.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.terraform]
}
