output "mysql_server_name" {
  description = "MySQL server name"
  value       = azurerm_mysql_flexible_server.main.name
}

output "mysql_fqdn" {
  description = "MySQL FQDN"
  value       = azurerm_mysql_flexible_server.main.fqdn
}

output "mysql_database_name" {
  description = "MySQL database name"
  value       = azurerm_mysql_flexible_database.flowlite.name
}

output "mysql_connection_string" {
  description = "MySQL connection string"
  value       = "Server=${azurerm_mysql_flexible_server.main.fqdn};Database=${azurerm_mysql_flexible_database.flowlite.name};Uid=${var.mysql_admin_username};Pwd=${var.mysql_admin_password};SslMode=Required;"
  sensitive   = true
}

output "mysql_connection_url" {
  description = "MySQL connection URL for Python/FastAPI"
  value       = "mysql+aiomysql://${var.mysql_admin_username}:${var.mysql_admin_password}@${azurerm_mysql_flexible_server.main.fqdn}:3306/${azurerm_mysql_flexible_database.flowlite.name}"
  sensitive   = true
}

output "redis_hostname" {
  description = "Redis hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "redis_port" {
  description = "Redis port"
  value       = azurerm_redis_cache.main.ssl_port
}

output "redis_primary_access_key" {
  description = "Redis primary access key"
  value       = azurerm_redis_cache.main.primary_access_key
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port},password=${azurerm_redis_cache.main.primary_access_key},ssl=True"
  sensitive   = true
}
