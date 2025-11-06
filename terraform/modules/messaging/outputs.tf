output "servicebus_namespace" {
  description = "Service Bus namespace name"
  value       = azurerm_servicebus_namespace.main.name
}

output "servicebus_namespace_id" {
  description = "Service Bus namespace ID"
  value       = azurerm_servicebus_namespace.main.id
}

output "servicebus_queue_name" {
  description = "Service Bus queue name"
  value       = azurerm_servicebus_queue.batch_processed.name
}

output "servicebus_queue_id" {
  description = "Service Bus queue ID"
  value       = azurerm_servicebus_queue.batch_processed.id
}

output "servicebus_connection_string" {
  description = "Service Bus connection string (manage policy)"
  value       = azurerm_servicebus_queue_authorization_rule.manage.primary_connection_string
  sensitive   = true
}

output "servicebus_send_connection_string" {
  description = "Service Bus connection string (send-only)"
  value       = azurerm_servicebus_queue_authorization_rule.send.primary_connection_string
  sensitive   = true
}

output "servicebus_listen_connection_string" {
  description = "Service Bus connection string (listen-only)"
  value       = azurerm_servicebus_queue_authorization_rule.listen.primary_connection_string
  sensitive   = true
}
