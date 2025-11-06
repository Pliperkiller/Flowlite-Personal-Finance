output "email_service_type" {
  description = "Type of email service deployed"
  value = var.use_azure_communication_services ? "Azure Communication Services" : (
    var.use_sendgrid ? "SendGrid" : (
      var.use_custom_smtp ? "Custom SMTP" : (
        var.deploy_mailhog_dev && var.environment == "dev" ? "MailHog (Dev)" : "None"
      )
    )
  )
}

output "azure_communication_service_id" {
  description = "Azure Communication Service ID"
  value       = var.use_azure_communication_services ? azurerm_communication_service.main[0].id : null
}

output "azure_communication_service_connection_string" {
  description = "Azure Communication Service connection string"
  value       = var.use_azure_communication_services ? azurerm_communication_service.main[0].primary_connection_string : null
  sensitive   = true
}

output "email_communication_service_id" {
  description = "Email Communication Service ID"
  value       = var.use_azure_communication_services ? azurerm_email_communication_service.main[0].id : null
}

output "mailhog_smtp_host" {
  description = "MailHog SMTP host (dev only)"
  value       = var.environment == "dev" && var.deploy_mailhog_dev ? azurerm_container_group.mailhog[0].ip_address : null
}

output "mailhog_smtp_port" {
  description = "MailHog SMTP port (dev only)"
  value       = var.environment == "dev" && var.deploy_mailhog_dev ? "1025" : null
}

output "mailhog_web_ui" {
  description = "MailHog Web UI (dev only)"
  value       = var.environment == "dev" && var.deploy_mailhog_dev ? "http://${azurerm_container_group.mailhog[0].ip_address}:8025" : null
}

output "smtp_configuration" {
  description = "SMTP configuration summary"
  value = {
    host      = var.use_custom_smtp ? var.smtp_host : (var.environment == "dev" && var.deploy_mailhog_dev ? azurerm_container_group.mailhog[0].ip_address : "")
    port      = var.use_custom_smtp ? var.smtp_port : (var.environment == "dev" && var.deploy_mailhog_dev ? "1025" : "")
    use_tls   = var.use_custom_smtp ? var.smtp_use_tls : false
    from_email = var.use_sendgrid ? var.sendgrid_from_email : var.smtp_from_email
  }
  sensitive = true
}
