# ================================
# Azure Kubernetes Service (AKS) - Option 1
# ================================

resource "azurerm_kubernetes_cluster" "main" {
  count               = var.use_aks ? 1 : 0
  name                = "${var.project_name}-${var.environment}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}"

  default_node_pool {
    name                = "default"
    node_count          = var.aks_node_count
    vm_size             = var.aks_node_vm_size
    vnet_subnet_id      = var.subnet_api_services_id
    enable_auto_scaling = true
    min_count           = var.aks_min_count
    max_count           = var.aks_max_count
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }

  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  tags = var.tags
}

# Grant AKS access to ACR
resource "azurerm_role_assignment" "aks_acr" {
  count                = var.use_aks ? 1 : 0
  principal_id         = azurerm_kubernetes_cluster.main[0].kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = var.acr_id
}

# ================================
# Azure Container Apps - Option 2 (Recommended for this use case)
# ================================

# Container Apps Environment
resource "azurerm_container_app_environment" "main" {
  count                      = !var.use_aks ? 1 : 0
  name                       = "${var.project_name}-${var.environment}-cae"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id

  tags = var.tags
}

# ================================
# Container Apps for Each Service
# ================================

# 1. Identity Service Container App
resource "azurerm_container_app" "identity_service" {
  count                        = !var.use_aks ? 1 : 0
  name                         = "${var.project_name}-identity-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_ids["identity_service"]]
  }

  template {
    min_replicas = var.service_replicas.identity_service
    max_replicas = var.service_replicas.identity_service * 5

    container {
      name   = "identity-service"
      image  = "${var.acr_login_server}/flowlite-identity:${var.docker_images.identity_service}"
      cpu    = 1.0
      memory = "2Gi"

      env {
        name  = "SPRING_PROFILES_ACTIVE"
        value = "azure"
      }

      env {
        name  = "SPRING_DATASOURCE_URL"
        value = "jdbc:${var.mysql_connection_string}"
      }

      env {
        name  = "SPRING_REDIS_HOST"
        value = split(":", var.redis_connection_string)[0]
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.application_insights_key
      }

      env {
        name  = "KEY_VAULT_URI"
        value = var.key_vault_id
      }
    }

    http_scale_rule {
      name                = "http-scaling"
      concurrent_requests = 100
    }
  }

  ingress {
    external_enabled = false
    target_port      = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = var.acr_login_server
    identity = var.managed_identity_ids["identity_service"]
  }

  tags = var.tags
}

# 2. Upload Service Container App
resource "azurerm_container_app" "upload_service" {
  count                        = !var.use_aks ? 1 : 0
  name                         = "${var.project_name}-upload-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_ids["upload_service"]]
  }

  template {
    min_replicas = var.service_replicas.upload_service
    max_replicas = var.service_replicas.upload_service * 5

    container {
      name   = "upload-service"
      image  = "${var.acr_login_server}/flowlite-upload:${var.docker_images.upload_service}"
      cpu    = 1.0
      memory = "2Gi"

      env {
        name  = "DATABASE_URL"
        value = var.mysql_connection_string
      }

      env {
        name  = "REDIS_URL"
        value = var.redis_connection_string
      }

      env {
        name  = "SERVICE_BUS_CONNECTION_STRING"
        value = var.servicebus_connection_string
      }

      env {
        name  = "IDENTITY_SERVICE_URL"
        value = !var.use_aks ? azurerm_container_app.identity_service[0].ingress[0].fqdn : "http://identity-service:8000"
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.application_insights_key
      }
    }

    http_scale_rule {
      name                = "http-scaling"
      concurrent_requests = 50
    }
  }

  ingress {
    external_enabled = false
    target_port      = 8001

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = var.acr_login_server
    identity = var.managed_identity_ids["upload_service"]
  }

  tags = var.tags
}

# 3. Data Service Container App
resource "azurerm_container_app" "data_service" {
  count                        = !var.use_aks ? 1 : 0
  name                         = "${var.project_name}-data-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_ids["data_service"]]
  }

  template {
    min_replicas = var.service_replicas.data_service
    max_replicas = var.service_replicas.data_service * 5

    container {
      name   = "data-service"
      image  = "${var.acr_login_server}/flowlite-data:${var.docker_images.data_service}"
      cpu    = 1.0
      memory = "2Gi"

      env {
        name  = "DATABASE_URL"
        value = var.mysql_connection_string
      }

      env {
        name  = "IDENTITY_SERVICE_URL"
        value = !var.use_aks ? azurerm_container_app.identity_service[0].ingress[0].fqdn : "http://identity-service:8000"
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.application_insights_key
      }
    }

    http_scale_rule {
      name                = "http-scaling"
      concurrent_requests = 100
    }
  }

  ingress {
    external_enabled = false
    target_port      = 8003

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = var.acr_login_server
    identity = var.managed_identity_ids["data_service"]
  }

  tags = var.tags
}

# 4. Insight Service Container App
resource "azurerm_container_app" "insight_service" {
  count                        = !var.use_aks ? 1 : 0
  name                         = "${var.project_name}-insight-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_ids["insight_service"]]
  }

  template {
    min_replicas = var.service_replicas.insight_service
    max_replicas = var.service_replicas.insight_service * 3

    container {
      name   = "insight-service"
      image  = "${var.acr_login_server}/flowlite-insight:${var.docker_images.insight_service}"
      cpu    = 2.0
      memory = "4Gi"

      env {
        name  = "DATABASE_URL"
        value = var.mysql_connection_string
      }

      env {
        name  = "SERVICE_BUS_CONNECTION_STRING"
        value = var.servicebus_connection_string
      }

      env {
        name  = "OLLAMA_BASE_URL"
        value = "http://${azurerm_linux_virtual_machine.ollama[0].private_ip_address}:11434"
      }

      env {
        name  = "OLLAMA_MODEL"
        value = var.ollama_model
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.application_insights_key
      }
    }
  }

  ingress {
    external_enabled = false
    target_port      = 8002

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server   = var.acr_login_server
    identity = var.managed_identity_ids["insight_service"]
  }

  tags = var.tags
}

# ================================
# Ollama LLM VM (GPU-enabled)
# ================================

# Public IP for Ollama VM (for management only)
resource "azurerm_public_ip" "ollama" {
  name                = "${var.project_name}-${var.environment}-ollama-pip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = var.tags
}

# Network Interface for Ollama VM
resource "azurerm_network_interface" "ollama" {
  name                = "${var.project_name}-${var.environment}-ollama-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_internal_services_id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.ollama.id
  }

  tags = var.tags
}

# Ollama VM
resource "azurerm_linux_virtual_machine" "ollama" {
  count               = 1
  name                = "${var.project_name}-${var.environment}-ollama-vm"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = var.ollama_vm_size
  admin_username      = "azureuser"

  network_interface_ids = [
    azurerm_network_interface.ollama.id,
  ]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub") # Change to your SSH public key path
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 128
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  # Custom data to install Ollama
  custom_data = base64encode(<<-EOF
    #!/bin/bash
    set -e

    # Update system
    apt-get update
    apt-get upgrade -y

    # Install NVIDIA drivers (for GPU VMs)
    apt-get install -y ubuntu-drivers-common
    ubuntu-drivers autoinstall

    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh

    # Install NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
    apt-get update
    apt-get install -y nvidia-container-toolkit
    systemctl restart docker

    # Install Ollama
    curl -fsSL https://ollama.com/install.sh | sh

    # Start Ollama service
    systemctl enable ollama
    systemctl start ollama

    # Pull the model
    ollama pull ${var.ollama_model}

    # Configure Ollama to listen on all interfaces
    echo "OLLAMA_HOST=0.0.0.0:11434" >> /etc/systemd/system/ollama.service.d/override.conf
    systemctl daemon-reload
    systemctl restart ollama
  EOF
  )

  tags = var.tags
}
