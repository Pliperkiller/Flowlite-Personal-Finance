# Email Configuration Guide - Flowlite

Esta guía explica cómo configurar el servicio de email para Flowlite en Azure.

## 📧 ¿Dónde se usa el email?

El **IdentityService** utiliza email para:
- ✉️ Verificación de cuenta (email de bienvenida)
- 🔑 Recuperación de contraseña
- 🔐 Códigos de verificación 2FA
- 📢 Notificaciones de cambios de contraseña

## 🎯 Opciones de Servicio de Email

### Opción 1: MailHog (Solo Desarrollo Local/Azure Dev) 🛠️

**Cuándo usar:**
- Desarrollo local
- Testing
- No necesitas enviar emails reales

**Ventajas:**
- ✅ Gratis
- ✅ No requiere configuración externa
- ✅ Web UI para ver emails capturados
- ✅ No envía emails reales (seguro para testing)

**Desventajas:**
- ❌ Solo para desarrollo
- ❌ Los emails no se entregan realmente

**Configuración en Terraform:**

```hcl
# terraform.tfvars
environment        = "dev"
deploy_mailhog_dev = true

# Deshabilitar otros servicios de email
use_azure_communication_services = false
use_sendgrid                     = false
use_custom_smtp                  = false
```

**Uso:**

Después del despliegue:
```bash
# Ver la IP de MailHog
terraform output mailhog_smtp_config

# Resultado:
# {
#   "host" = "10.0.2.15"
#   "port" = "1025"
# }

# Acceder al Web UI (necesitas VPN o túnel SSH)
terraform output mailhog_web_ui
# http://10.0.2.15:8025
```

**Configurar IdentityService:**

```properties
# application.properties
spring.mail.host=${SMTP_HOST}      # Desde Key Vault
spring.mail.port=${SMTP_PORT}      # 1025
spring.mail.username=              # Vacío
spring.mail.password=              # Vacío
spring.mail.properties.mail.smtp.auth=false
spring.mail.properties.mail.smtp.starttls.enable=false
```

---

### Opción 2: Gmail/Custom SMTP (Desarrollo/Staging) 📮

**Cuándo usar:**
- Staging/Pre-producción
- Pruebas con emails reales
- Tienes cuenta de Gmail u otro servicio SMTP

**Ventajas:**
- ✅ Emails reales entregados
- ✅ Fácil configuración
- ✅ Gratis con Gmail (con límites)

**Desventajas:**
- ⚠️ Límites de envío (Gmail: 500/día)
- ⚠️ Requiere configuración de "App Password"
- ⚠️ Puede marcar como spam

**Configuración con Gmail:**

1. **Habilitar App Password en Gmail:**
   ```
   1. Ve a https://myaccount.google.com/security
   2. Habilita "Verificación en 2 pasos"
   3. Ve a "Contraseñas de aplicaciones"
   4. Genera una contraseña para "Mail"
   5. Copia la contraseña generada (ej: "abcd efgh ijkl mnop")
   ```

2. **Configurar en Terraform:**
   ```hcl
   # terraform.tfvars
   use_custom_smtp = true
   smtp_host       = "smtp.gmail.com"
   smtp_port       = "587"
   smtp_username   = "tu-email@gmail.com"
   smtp_password   = "abcd efgh ijkl mnop"  # App Password de Gmail
   smtp_from_email = "noreply@flowlite.com"
   smtp_use_tls    = true
   ```

3. **Desplegar:**
   ```bash
   terraform apply
   ```

**Configuración con Office 365:**

```hcl
# terraform.tfvars
use_custom_smtp = true
smtp_host       = "smtp.office365.com"
smtp_port       = "587"
smtp_username   = "tu-email@tuempresa.com"
smtp_password   = "tu-password"
smtp_from_email = "noreply@tuempresa.com"
smtp_use_tls    = true
```

---

### Opción 3: SendGrid (Producción/Staging) 🚀

**Cuándo usar:**
- Producción
- Volumen medio/alto de emails
- Necesitas analíticas y reportes

**Ventajas:**
- ✅ Alta entregabilidad
- ✅ Analíticas detalladas
- ✅ API poderosa
- ✅ Fácil integración

**Desventajas:**
- 💰 Costo: Free tier (100 emails/día), luego $15-90/mes
- ⚠️ Requiere verificación de dominio

**Setup:**

1. **Crear cuenta SendGrid:**
   - Ve a https://sendgrid.com/
   - Crea cuenta gratuita
   - Verifica tu email

2. **Obtener API Key:**
   ```
   1. Login en SendGrid Dashboard
   2. Settings → API Keys
   3. Create API Key
   4. Nombre: "Flowlite Production"
   5. Full Access
   6. Copia la API Key (SG.xxxxxxxxxxxxx)
   ```

3. **Verificar dominio (recomendado):**
   ```
   1. Settings → Sender Authentication
   2. Domain Authentication
   3. Sigue las instrucciones para agregar registros DNS
   ```

4. **Configurar en Terraform:**
   ```hcl
   # terraform.tfvars
   use_sendgrid        = true
   sendgrid_api_key    = "SG.xxxxxxxxxxxxx"
   sendgrid_from_email = "noreply@flowlite.com"

   # Deshabilitar otros servicios
   use_azure_communication_services = false
   use_custom_smtp                  = false
   ```

5. **Desplegar:**
   ```bash
   terraform apply
   ```

**Configurar IdentityService para SendGrid:**

Actualizar `identifyservice` para usar SendGrid API en lugar de SMTP:

```java
// Agregar dependencia en build.gradle
implementation 'com.sendgrid:sendgrid-java:4.9.3'

// Configuración
@Value("${sendgrid.api.key}")
private String sendGridApiKey;

public void sendEmail(String to, String subject, String body) {
    Email from = new Email("noreply@flowlite.com");
    Email toEmail = new Email(to);
    Content content = new Content("text/html", body);
    Mail mail = new Mail(from, subject, toEmail, content);

    SendGrid sg = new SendGrid(sendGridApiKey);
    Request request = new Request();
    request.setMethod(Method.POST);
    request.setEndpoint("mail/send");
    request.setBody(mail.build());
    Response response = sg.api(request);
}
```

---

### Opción 4: Azure Communication Services (Producción Recomendada) ☁️

**Cuándo usar:**
- Producción en Azure
- Mejor integración con el ecosistema Azure
- Necesitas escalabilidad

**Ventajas:**
- ✅ Integración nativa con Azure
- ✅ Managed Identity support
- ✅ Alta escalabilidad
- ✅ Cumplimiento y seguridad

**Desventajas:**
- 💰 Costo: ~$0.0012 por email
- ⚠️ Requiere verificación de dominio
- ⚠️ Servicio en preview

**Setup:**

1. **Configurar en Terraform:**
   ```hcl
   # terraform.tfvars
   use_azure_communication_services = true
   email_domain                     = "flowlite.com"  # Tu dominio

   # Deshabilitar otros servicios
   use_sendgrid    = false
   use_custom_smtp = false
   ```

2. **Desplegar:**
   ```bash
   terraform apply
   ```

3. **Verificar dominio en Azure Portal:**
   ```
   1. Ve a Azure Portal
   2. Busca "Communication Services"
   3. Selecciona tu Email Communication Service
   4. Email → Domains
   5. Sigue las instrucciones para verificar tu dominio
   6. Agrega registros DNS SPF, DKIM, DMARC
   ```

4. **Obtener connection string:**
   ```bash
   az keyvault secret show \
     --vault-name $(terraform output -raw key_vault_name) \
     --name email-connection-string
   ```

**Configurar IdentityService para Azure Communication Services:**

```java
// Agregar dependencia en build.gradle
implementation 'com.azure:azure-communication-email:1.0.0'

// Configuración
@Value("${azure.communication.connection-string}")
private String communicationConnectionString;

public void sendEmail(String to, String subject, String body) {
    EmailClient emailClient = new EmailClientBuilder()
        .connectionString(communicationConnectionString)
        .buildClient();

    EmailMessage message = new EmailMessage()
        .setSenderAddress("noreply@flowlite.com")
        .setToRecipients(to)
        .setSubject(subject)
        .setBodyHtml(body);

    SyncPoller<EmailSendResult, EmailSendResult> poller =
        emailClient.beginSend(message);

    EmailSendResult result = poller.getFinalResult();
}
```

---

## 🔧 Configuración del IdentityService

El IdentityService necesita las credenciales SMTP desde Azure Key Vault:

### Variables de entorno necesarias:

```bash
# Para SMTP (Gmail, Custom SMTP, MailHog)
SPRING_MAIL_HOST=<from Key Vault: smtp-host>
SPRING_MAIL_PORT=<from Key Vault: smtp-port>
SPRING_MAIL_USERNAME=<from Key Vault: smtp-username>
SPRING_MAIL_PASSWORD=<from Key Vault: smtp-password>
SPRING_MAIL_PROPERTIES_MAIL_SMTP_AUTH=true
SPRING_MAIL_PROPERTIES_MAIL_SMTP_STARTTLS_ENABLE=true

# Para SendGrid
SENDGRID_API_KEY=<from Key Vault: sendgrid-api-key>

# Para Azure Communication Services
AZURE_COMMUNICATION_CONNECTION_STRING=<from Key Vault: email-connection-string>
```

### Actualizar Container App configuration:

En el módulo de compute, agregar estas variables de entorno al IdentityService:

```hcl
env {
  name  = "SPRING_MAIL_HOST"
  secret_name = "smtp-host"
}

env {
  name  = "SPRING_MAIL_PORT"
  secret_name = "smtp-port"
}

# ... más variables según el servicio elegido
```

---

## 📊 Comparación de Opciones

| Característica | MailHog | Gmail SMTP | SendGrid | Azure Comm Services |
|----------------|---------|------------|----------|---------------------|
| **Costo** | Gratis | Gratis | $0-90/mes | $0.0012/email |
| **Límite diario** | Ilimitado* | 500 emails | 100-100K+ | Ilimitado |
| **Entregabilidad** | N/A (mock) | Media | Alta | Alta |
| **Setup** | Automático | 5 min | 10 min | 15 min |
| **Producción** | ❌ No | ⚠️ Limitado | ✅ Sí | ✅ Sí |
| **Analíticas** | Web UI | No | ✅ Sí | ✅ Sí |
| **Azure Native** | No | No | No | ✅ Sí |

*MailHog no envía emails reales

---

## 🎯 Recomendaciones por Ambiente

### Desarrollo Local
```hcl
# Usa Docker Compose local (ya configurado en el proyecto)
# No desplegar email service en Azure para dev local
```

### Desarrollo en Azure
```hcl
deploy_mailhog_dev = true
```

### Staging
```hcl
use_custom_smtp = true  # Gmail o Office 365
# O
use_sendgrid = true     # Free tier
```

### Producción
```hcl
use_azure_communication_services = true  # Recomendado
# O
use_sendgrid = true                      # Alternativa popular
```

---

## 🔍 Troubleshooting

### MailHog no es accesible

```bash
# Verificar que el container está corriendo
az container show \
  --resource-group $(terraform output -raw resource_group_name) \
  --name flowlite-mailhog-dev

# Ver logs
az container logs \
  --resource-group $(terraform output -raw resource_group_name) \
  --name flowlite-mailhog-dev

# Crear túnel SSH para acceder al Web UI (desde VM en la VNet)
ssh -L 8025:10.0.2.15:8025 azureuser@<vm-public-ip>
# Luego accede a http://localhost:8025
```

### Gmail rechaza conexión

```
Error: 535-5.7.8 Username and Password not accepted
```

**Solución:**
1. Habilita "Verificación en 2 pasos" en tu cuenta Google
2. Genera "App Password" específica
3. Usa la app password en lugar de tu contraseña real

### SendGrid emails van a spam

**Solución:**
1. Verifica tu dominio en SendGrid
2. Configura SPF, DKIM, DMARC en tu DNS
3. Usa un dominio real (no @gmail.com en el From)

### Azure Communication Services no entrega emails

**Solución:**
1. Verifica que el dominio está verificado en Azure Portal
2. Revisa los logs en Application Insights
3. Verifica los registros DNS (SPF, DKIM, DMARC)

---

## 📚 Referencias

- [Azure Communication Services - Email](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [MailHog GitHub](https://github.com/mailhog/MailHog)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
