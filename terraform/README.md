# Flowlite Azure Infrastructure - Terraform

Este directorio contiene el código de Terraform para desplegar la infraestructura completa de Flowlite en Azure.

## 📋 Requisitos Previos

### Software Requerido

- [Terraform](https://www.terraform.io/downloads.html) >= 1.5.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) >= 2.50.0
- SSH Key pair (para acceso a VM de Ollama)

### Credenciales de Azure

```bash
# Login a Azure
az login

# Verificar la suscripción activa
az account show

# Cambiar suscripción si es necesario
az account set --subscription "SUBSCRIPTION_ID"
```

## 🏗️ Estructura del Proyecto

```
terraform/
├── main.tf                    # Configuración principal
├── variables.tf               # Variables globales
├── outputs.tf                 # Outputs globales
├── versions.tf                # Versiones de providers
├── terraform.tfvars.example   # Ejemplo de variables (copiar a terraform.tfvars)
├── README.md                  # Esta guía
│
├── modules/
│   ├── networking/            # VNet, Subnets, NSGs, NAT Gateway
│   ├── security/              # Key Vault, Managed Identities
│   ├── database/              # MySQL, Redis
│   ├── messaging/             # Service Bus
│   ├── monitoring/            # Application Insights, Log Analytics
│   └── compute/               # AKS/Container Apps, Ollama VM
│
└── environments/
    ├── dev/                   # Configuración de desarrollo
    ├── staging/               # Configuración de staging
    └── prod/                  # Configuración de producción
```

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
cd terraform

# Copiar y editar variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# Generar SSH key si no existe
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

### 2. Editar Variables

Edita `terraform.tfvars` con tus valores:

```hcl
# Mínimo requerido
project_name         = "flowlite"
environment          = "dev"
location             = "eastus"
mysql_admin_username = "flowliteadmin"
mysql_admin_password = "TU_PASSWORD_SEGURO_AQUI"
```

### 3. Inicializar Terraform

```bash
# Inicializar providers y módulos
terraform init

# (Opcional) Validar configuración
terraform validate

# (Opcional) Formatear código
terraform fmt -recursive
```

### 4. Planificar Despliegue

```bash
# Ver qué recursos se crearán
terraform plan -out=tfplan

# Guardar el plan para revisión
terraform show tfplan > plan.txt
```

### 5. Aplicar Infraestructura

```bash
# Aplicar el plan
terraform apply tfplan

# O aplicar directamente (con confirmación)
terraform apply
```

⏱️ **Tiempo estimado de despliegue: 15-30 minutos**

## 📊 Outputs

Después del despliegue, verás outputs importantes:

```bash
# Ver todos los outputs
terraform output

# Ver un output específico
terraform output app_gateway_public_ip

# Ver outputs sensibles (connection strings)
terraform output -raw mysql_connection_string
```

## 🔧 Comandos Útiles

### Gestión de Infraestructura

```bash
# Ver estado actual
terraform show

# Listar recursos
terraform state list

# Inspeccionar un recurso específico
terraform state show azurerm_resource_group.main

# Refrescar estado (sincronizar con Azure)
terraform refresh

# Destruir infraestructura (¡CUIDADO!)
terraform destroy
```

### Debugging

```bash
# Habilitar logs detallados
export TF_LOG=DEBUG
export TF_LOG_PATH=terraform.log

# Ver logs
tail -f terraform.log

# Deshabilitar logs
unset TF_LOG
unset TF_LOG_PATH
```

### Gestión de State

```bash
# Ver estado actual
terraform state list

# Importar recurso existente
terraform import azurerm_resource_group.main /subscriptions/SUBSCRIPTION_ID/resourceGroups/flowlite-dev-rg

# Remover recurso del state (sin eliminarlo en Azure)
terraform state rm azurerm_resource_group.main
```

## 🔐 Gestión de Secretos

### Opción 1: Variables de Entorno

```bash
export TF_VAR_mysql_admin_password="TU_PASSWORD"
export TF_VAR_mysql_admin_username="flowliteadmin"

terraform apply
```

### Opción 2: Archivo .tfvars.local (No versionado)

```bash
# Crear archivo local (ya está en .gitignore)
cat > terraform.tfvars.local <<EOF
mysql_admin_username = "flowliteadmin"
mysql_admin_password = "PASSWORD_SEGURO"
EOF

# Aplicar con archivo local
terraform apply -var-file=terraform.tfvars.local
```

### Opción 3: Azure Key Vault

Los secretos se almacenan automáticamente en Azure Key Vault después del despliegue.

```bash
# Obtener secreto de Key Vault
az keyvault secret show \
  --vault-name $(terraform output -raw key_vault_name) \
  --name mysql-connection-string
```

## 🌍 Ambientes Múltiples

### Usando Workspaces

```bash
# Crear workspace para staging
terraform workspace new staging

# Cambiar a workspace
terraform workspace select staging

# Listar workspaces
terraform workspace list

# Aplicar en workspace actual
terraform apply -var-file=environments/staging/terraform.tfvars
```

### Usando Directorios Separados

```bash
# Desarrollo
cd environments/dev
terraform init
terraform apply

# Producción
cd environments/prod
terraform init
terraform apply
```

## 🔄 Backend Remoto (Recomendado para Producción)

### Configurar Azure Storage Backend

```bash
# Crear resource group para state
az group create --name terraform-state-rg --location eastus

# Crear storage account
az storage account create \
  --name tfstateflowlite \
  --resource-group terraform-state-rg \
  --location eastus \
  --sku Standard_LRS \
  --encryption-services blob

# Crear container
az storage container create \
  --name tfstate \
  --account-name tfstateflowlite
```

### Actualizar versions.tf

Descomentar y configurar en `versions.tf`:

```hcl
backend "azurerm" {
  resource_group_name  = "terraform-state-rg"
  storage_account_name = "tfstateflowlite"
  container_name       = "tfstate"
  key                  = "flowlite.terraform.tfstate"
}
```

### Migrar State Existente

```bash
# Reinicializar con nuevo backend
terraform init -migrate-state
```

## 🐳 Construir y Subir Imágenes Docker

Después de desplegar la infraestructura:

```bash
# Obtener credenciales de ACR
ACR_NAME=$(terraform output -raw acr_name)
az acr login --name $ACR_NAME

# Construir imágenes (desde el root del proyecto)
cd ..

# Identity Service
docker build -t $ACR_NAME.azurecr.io/flowlite-identity:latest ./identifyservice
docker push $ACR_NAME.azurecr.io/flowlite-identity:latest

# Upload Service
docker build -t $ACR_NAME.azurecr.io/flowlite-upload:latest ./uploadservice
docker push $ACR_NAME.azurecr.io/flowlite-upload:latest

# Data Service
docker build -t $ACR_NAME.azurecr.io/flowlite-data:latest ./dataservice
docker push $ACR_NAME.azurecr.io/flowlite-data:latest

# Insight Service
docker build -t $ACR_NAME.azurecr.io/flowlite-insight:latest ./InsightService
docker push $ACR_NAME.azurecr.io/flowlite-insight:latest
```

## 🔍 Verificación Post-Despliegue

### 1. Verificar Recursos en Azure

```bash
# Ver resource group
az group show --name $(terraform output -raw resource_group_name)

# Listar todos los recursos
az resource list \
  --resource-group $(terraform output -raw resource_group_name) \
  --output table
```

### 2. Verificar Conectividad

```bash
# MySQL
mysql -h $(terraform output -raw mysql_fqdn) \
  -u flowliteadmin -p flowlite_db

# Redis
redis-cli -h $(terraform output -raw redis_hostname) \
  -p $(terraform output -raw redis_port) \
  --tls \
  -a "$(terraform output -raw redis_primary_access_key)"

# Service Bus
# Verificar desde Azure Portal o con Azure CLI
```

### 3. Verificar Servicios

```bash
# Application Gateway IP
APP_GW_IP=$(terraform output -raw app_gateway_public_ip)

# Health checks
curl http://$APP_GW_IP/health
```

## 📈 Monitoreo

### Application Insights

```bash
# Obtener instrumentation key
terraform output -raw application_insights_instrumentation_key

# Ver logs en tiempo real
az monitor app-insights query \
  --app $(terraform output -raw application_insights_name) \
  --analytics-query "requests | take 10"
```

### Log Analytics

```bash
# Ver logs de contenedores
az monitor log-analytics query \
  -w $(terraform output -raw log_analytics_workspace_id) \
  --analytics-query "ContainerLog | take 10"
```

## 💰 Estimación de Costos

### Desarrollo (configuración por defecto)

| Recurso | Costo Mensual Estimado |
|---------|------------------------|
| Application Gateway WAF v2 | $250 |
| Container Apps | $100 |
| MySQL B_Standard_B2s | $85 |
| Redis Standard C1 | $15 |
| Service Bus Standard | $10 |
| Ollama VM NC6s_v3 | $900 |
| Container Registry Basic | $5 |
| Key Vault | $5 |
| Application Insights | $50 |
| **TOTAL** | **~$1,420/mes** |

### Producción (configuración recomendada)

```hcl
# En terraform.tfvars para producción
mysql_sku_name = "GP_Standard_D2ds_v4"
mysql_high_availability_enabled = true
redis_sku_name = "Premium"
redis_capacity = 1
servicebus_sku = "Premium"
enable_ddos_protection = true
```

**Costo estimado: ~$2,400-3,000/mes**

### Optimización de Costos

1. **VM Ollama → Azure OpenAI**: Ahorra ~$850/mes
2. **Reserved Instances**: Ahorra 30-50% en VMs y databases
3. **Auto-shutdown**: Deshabilita recursos fuera de horario laboral
4. **Container Apps scale-to-zero**: Solo paga por uso real

## 🐛 Troubleshooting

### Error: "Quota exceeded"

```bash
# Verificar quotas
az vm list-usage --location eastus -o table

# Solicitar aumento de quota
# Azure Portal → Subscriptions → Usage + quotas
```

### Error: "Insufficient permissions"

```bash
# Verificar rol actual
az role assignment list --assignee $(az account show --query user.name -o tsv)

# Necesitas rol "Contributor" o "Owner"
```

### Error: "Backend initialization failed"

```bash
# Eliminar state local y reinicializar
rm -rf .terraform
rm .terraform.lock.hcl
terraform init
```

### Error: "Resource already exists"

```bash
# Importar recurso existente
terraform import azurerm_resource_group.main /subscriptions/SUB_ID/resourceGroups/flowlite-dev-rg
```

## 📚 Recursos Adicionales

- [Azure Terraform Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
- [Flowlite Architecture Diagram](../docs/AZURE_ARCHITECTURE.md)

## 🤝 Contribuciones

Para modificar la infraestructura:

1. Crear un branch: `git checkout -b feature/new-resource`
2. Hacer cambios en Terraform
3. Ejecutar `terraform plan` y verificar
4. Commit y push
5. Crear Pull Request

## ⚠️ Advertencias Importantes

1. **NUNCA** comitear `terraform.tfvars` con credenciales reales
2. **SIEMPRE** usar `terraform plan` antes de `apply`
3. **CUIDADO** con `terraform destroy` en producción
4. **HABILITAR** Private Endpoints en producción
5. **CONFIGURAR** backups y disaster recovery
6. **ROTAR** secretos y credenciales regularmente

## 📞 Soporte

Para problemas o preguntas:

- Issues: [GitHub Issues](https://github.com/tu-org/flowlite/issues)
- Documentación: [docs/AZURE_ARCHITECTURE.md](../docs/AZURE_ARCHITECTURE.md)
- Azure Support: [Azure Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)

---

**¡Listo para desplegar! 🚀**

```bash
terraform init && terraform plan && terraform apply
```
