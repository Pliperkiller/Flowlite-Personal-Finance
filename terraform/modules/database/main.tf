# ================================
# Azure Database for MySQL Flexible Server
# ================================

resource "azurerm_mysql_flexible_server" "main" {
  name                   = "${var.project_name}-mysql-${var.random_suffix}"
  location               = var.location
  resource_group_name    = var.resource_group_name
  administrator_login    = var.mysql_admin_username
  administrator_password = var.mysql_admin_password

  sku_name   = var.mysql_sku_name
  version    = var.mysql_version

  backup_retention_days        = var.mysql_backup_retention_days
  geo_redundant_backup_enabled = false # Set to true for production

  # High Availability Configuration (Zone Redundant)
  dynamic "high_availability" {
    for_each = var.mysql_high_availability_enabled ? [1] : []
    content {
      mode                      = "ZoneRedundant"
      standby_availability_zone = "2"
    }
  }

  storage {
    size_gb = var.mysql_storage_size_gb
    iops    = 360
    auto_grow_enabled = true
  }

  tags = var.tags
}

# MySQL Database
resource "azurerm_mysql_flexible_database" "flowlite" {
  name                = "flowlite_db"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.main.name
  charset             = "utf8mb4"
  collation           = "utf8mb4_unicode_ci"
}

# MySQL Firewall Rule - Allow Azure Services
resource "azurerm_mysql_flexible_server_firewall_rule" "azure_services" {
  name                = "AllowAzureServices"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.main.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
}

# MySQL Configuration Parameters
resource "azurerm_mysql_flexible_server_configuration" "max_connections" {
  name                = "max_connections"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.main.name
  value               = "200"
}

resource "azurerm_mysql_flexible_server_configuration" "connect_timeout" {
  name                = "connect_timeout"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.main.name
  value               = "30"
}

resource "azurerm_mysql_flexible_server_configuration" "wait_timeout" {
  name                = "wait_timeout"
  resource_group_name = var.resource_group_name
  server_name         = azurerm_mysql_flexible_server.main.name
  value               = "28800"
}

# ================================
# Azure Cache for Redis
# ================================

resource "azurerm_redis_cache" "main" {
  name                = "${var.project_name}-redis-${var.random_suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku_name

  # Enable non-SSL port for development (disable in production)
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  # Redis Configuration
  redis_configuration {
    maxmemory_policy = "allkeys-lru"
    maxmemory_delta  = 2
  }

  # Enable Redis persistence for Premium tier
  dynamic "redis_configuration" {
    for_each = var.redis_sku_name == "Premium" ? [1] : []
    content {
      enable_authentication = true
      maxmemory_reserved    = 2
      maxmemory_delta       = 2
      maxmemory_policy      = "allkeys-lru"
    }
  }

  tags = var.tags
}

# ================================
# Private Endpoints (Recommended for Production)
# ================================

# Private Endpoint for MySQL (Commented - Enable for production)
# resource "azurerm_private_endpoint" "mysql" {
#   name                = "${var.project_name}-mysql-pe"
#   location            = var.location
#   resource_group_name = var.resource_group_name
#   subnet_id           = var.subnet_data_layer_id
#
#   private_service_connection {
#     name                           = "${var.project_name}-mysql-psc"
#     private_connection_resource_id = azurerm_mysql_flexible_server.main.id
#     is_manual_connection           = false
#     subresource_names              = ["mysqlServer"]
#   }
#
#   tags = var.tags
# }

# Private Endpoint for Redis (Commented - Enable for production)
# resource "azurerm_private_endpoint" "redis" {
#   name                = "${var.project_name}-redis-pe"
#   location            = var.location
#   resource_group_name = var.resource_group_name
#   subnet_id           = var.subnet_data_layer_id
#
#   private_service_connection {
#     name                           = "${var.project_name}-redis-psc"
#     private_connection_resource_id = azurerm_redis_cache.main.id
#     is_manual_connection           = false
#     subresource_names              = ["redisCache"]
#   }
#
#   tags = var.tags
# }
