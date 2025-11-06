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

variable "key_vault_id" {
  description = "Key Vault ID for storing secrets"
  type        = string
}

variable "subnet_internal_services_id" {
  description = "Internal services subnet ID (for MailHog dev)"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}

# ================================
# Azure Communication Services
# ================================

variable "use_azure_communication_services" {
  description = "Use Azure Communication Services for email"
  type        = bool
  default     = false
}

variable "email_domain" {
  description = "Email domain for Azure Communication Services (e.g., flowlite.com)"
  type        = string
  default     = ""
}

# ================================
# SendGrid
# ================================

variable "use_sendgrid" {
  description = "Use SendGrid for email"
  type        = bool
  default     = false
}

variable "sendgrid_api_key" {
  description = "SendGrid API key (store in environment variable)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "sendgrid_from_email" {
  description = "SendGrid from email address"
  type        = string
  default     = "noreply@flowlite.com"
}

# ================================
# Custom SMTP
# ================================

variable "use_custom_smtp" {
  description = "Use custom SMTP server"
  type        = bool
  default     = false
}

variable "smtp_host" {
  description = "SMTP server host"
  type        = string
  default     = ""
}

variable "smtp_port" {
  description = "SMTP server port"
  type        = string
  default     = "587"
}

variable "smtp_username" {
  description = "SMTP username"
  type        = string
  default     = ""
  sensitive   = true
}

variable "smtp_password" {
  description = "SMTP password"
  type        = string
  default     = ""
  sensitive   = true
}

variable "smtp_from_email" {
  description = "SMTP from email address"
  type        = string
  default     = "noreply@flowlite.com"
}

variable "smtp_use_tls" {
  description = "Use TLS for SMTP"
  type        = bool
  default     = true
}

# ================================
# Development: MailHog
# ================================

variable "deploy_mailhog_dev" {
  description = "Deploy MailHog in development environment (Azure Container Instance)"
  type        = bool
  default     = false
}
