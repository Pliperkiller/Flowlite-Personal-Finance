# ================================
# Azure Service Bus Namespace
# ================================

resource "azurerm_servicebus_namespace" "main" {
  name                = "${var.project_name}-${var.environment}-sb"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.servicebus_sku
  capacity            = var.servicebus_sku == "Premium" ? 1 : 0

  tags = var.tags
}

# ================================
# Service Bus Queue for Batch Processing
# ================================

resource "azurerm_servicebus_queue" "batch_processed" {
  name         = "batch_processed"
  namespace_id = azurerm_servicebus_namespace.main.id

  # Enable dead letter queue
  dead_lettering_on_message_expiration = true
  max_delivery_count                   = 10

  # Message TTL (7 days)
  default_message_ttl = "P7D"

  # Enable duplicate detection
  requires_duplicate_detection = true
  duplicate_detection_history_time_window = "PT10M"

  # Enable sessions for ordered processing (optional)
  requires_session = false

  # Max size
  max_size_in_megabytes = var.servicebus_sku == "Premium" ? 5120 : 1024
}

# ================================
# Authorization Rules
# ================================

# Send-only policy for UploadService
resource "azurerm_servicebus_queue_authorization_rule" "send" {
  name     = "SendPolicy"
  queue_id = azurerm_servicebus_queue.batch_processed.id

  listen = false
  send   = true
  manage = false
}

# Listen-only policy for InsightService
resource "azurerm_servicebus_queue_authorization_rule" "listen" {
  name     = "ListenPolicy"
  queue_id = azurerm_servicebus_queue.batch_processed.id

  listen = true
  send   = false
  manage = false
}

# Manage policy for admin operations
resource "azurerm_servicebus_queue_authorization_rule" "manage" {
  name     = "ManagePolicy"
  queue_id = azurerm_servicebus_queue.batch_processed.id

  listen = true
  send   = true
  manage = true
}

# ================================
# Private Endpoint (Premium tier only)
# ================================

# resource "azurerm_private_endpoint" "servicebus" {
#   count               = var.servicebus_sku == "Premium" ? 1 : 0
#   name                = "${var.project_name}-sb-pe"
#   location            = var.location
#   resource_group_name = var.resource_group_name
#   subnet_id           = var.subnet_data_layer_id
#
#   private_service_connection {
#     name                           = "${var.project_name}-sb-psc"
#     private_connection_resource_id = azurerm_servicebus_namespace.main.id
#     is_manual_connection           = false
#     subresource_names              = ["namespace"]
#   }
#
#   tags = var.tags
# }
