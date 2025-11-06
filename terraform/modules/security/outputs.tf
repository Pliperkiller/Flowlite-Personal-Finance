output "key_vault_id" {
  description = "Key Vault ID"
  value       = azurerm_key_vault.main.id
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}

output "managed_identity_ids" {
  description = "Managed Identity IDs"
  value = {
    identity_service = azurerm_user_assigned_identity.identity_service.id
    upload_service   = azurerm_user_assigned_identity.upload_service.id
    data_service     = azurerm_user_assigned_identity.data_service.id
    insight_service  = azurerm_user_assigned_identity.insight_service.id
  }
}

output "managed_identity_principal_ids" {
  description = "Managed Identity Principal IDs"
  value = {
    identity_service = azurerm_user_assigned_identity.identity_service.principal_id
    upload_service   = azurerm_user_assigned_identity.upload_service.principal_id
    data_service     = azurerm_user_assigned_identity.data_service.principal_id
    insight_service  = azurerm_user_assigned_identity.insight_service.principal_id
  }
}

output "managed_identity_client_ids" {
  description = "Managed Identity Client IDs"
  value = {
    identity_service = azurerm_user_assigned_identity.identity_service.client_id
    upload_service   = azurerm_user_assigned_identity.upload_service.client_id
    data_service     = azurerm_user_assigned_identity.data_service.client_id
    insight_service  = azurerm_user_assigned_identity.insight_service.client_id
  }
}

output "jwt_secret_name" {
  description = "JWT secret name in Key Vault"
  value       = azurerm_key_vault_secret.jwt_secret.name
}
