output "aks_cluster_name" {
  description = "AKS cluster name"
  value       = var.use_aks ? azurerm_kubernetes_cluster.main[0].name : null
}

output "aks_cluster_fqdn" {
  description = "AKS cluster FQDN"
  value       = var.use_aks ? azurerm_kubernetes_cluster.main[0].fqdn : null
}

output "container_app_environment_name" {
  description = "Container Apps Environment name"
  value       = !var.use_aks ? azurerm_container_app_environment.main[0].name : null
}

output "container_app_environment_id" {
  description = "Container Apps Environment ID"
  value       = !var.use_aks ? azurerm_container_app_environment.main[0].id : null
}

output "service_endpoints" {
  description = "Service endpoints"
  value = !var.use_aks ? {
    identity_service = azurerm_container_app.identity_service[0].ingress[0].fqdn
    upload_service   = azurerm_container_app.upload_service[0].ingress[0].fqdn
    data_service     = azurerm_container_app.data_service[0].ingress[0].fqdn
    insight_service  = azurerm_container_app.insight_service[0].ingress[0].fqdn
  } : {}
}

output "ollama_vm_private_ip" {
  description = "Ollama VM private IP address"
  value       = azurerm_linux_virtual_machine.ollama[0].private_ip_address
}

output "ollama_vm_public_ip" {
  description = "Ollama VM public IP address"
  value       = azurerm_public_ip.ollama.ip_address
}
