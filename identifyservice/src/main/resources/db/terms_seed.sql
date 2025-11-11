-- ===========================================
-- SEED DE TÉRMINOS Y CONDICIONES INICIALES
-- Flowlite Personal Finance Application
-- ===========================================
--
-- Este script inserta la versión inicial de Términos de Servicio
-- y Política de Privacidad en la base de datos.
--
-- Versión: v1.0_2025-01-15
-- Fecha: 2025-01-15
-- ===========================================

USE identifyservice;

-- Insertar Términos de Servicio v1.0
INSERT INTO TermsVersion (
    id,
    version_number,
    type,
    title,
    content_text,
    content_url,
    change_summary,
    is_major_change,
    requires_reacceptance,
    status,
    effective_date,
    created_at,
    published_at,
    created_by,
    active
) VALUES (
    UNHEX(REPLACE('11111111-1111-1111-1111-111111111111', '-', '')),
    'v1.0_2025-01-15',
    'TERMS_OF_SERVICE',
    'Flowlite - Términos de Servicio',
    'TÉRMINOS DE SERVICIO - FLOWLITE PERSONAL FINANCE

1. ACEPTACIÓN DE LOS TÉRMINOS
Al acceder y utilizar Flowlite, usted acepta estar sujeto a estos Términos de Servicio y todas las leyes y reglamentos aplicables.

2. USO DEL SERVICIO
Flowlite es una aplicación de gestión de finanzas personales que le permite:
- Registrar y categorizar transacciones financieras
- Visualizar su historial financiero
- Generar reportes y estadísticas
- Administrar su información personal

3. CUENTA DE USUARIO
- Debe proporcionar información precisa y completa al registrarse
- Es responsable de mantener la confidencialidad de su cuenta
- Debe notificar inmediatamente cualquier uso no autorizado

4. PRIVACIDAD Y SEGURIDAD
- Sus datos están protegidos según nuestra Política de Privacidad
- Implementamos medidas de seguridad técnicas y organizativas
- No compartimos su información con terceros sin su consentimiento

5. RESPONSABILIDADES DEL USUARIO
- Usar el servicio de manera legal y ética
- No intentar acceder a datos de otros usuarios
- Mantener su información actualizada
- No realizar actividades que comprometan la seguridad

6. LIMITACIÓN DE RESPONSABILIDAD
Flowlite se proporciona "tal cual" sin garantías de ningún tipo. No somos responsables por:
- Pérdidas financieras basadas en información de la aplicación
- Interrupciones del servicio
- Errores en cálculos o reportes

7. MODIFICACIONES
Nos reservamos el derecho de modificar estos términos. Los cambios importantes requerirán su aceptación explícita.

8. TERMINACIÓN
Podemos suspender o terminar su cuenta si viola estos términos.

9. LEY APLICABLE
Estos términos se rigen por las leyes de Colombia.

10. CONTACTO
Para preguntas sobre estos términos: support@flowlite.com

Fecha de vigencia: 15 de Enero de 2025
Última actualización: 15 de Enero de 2025',
    'https://flowlite.com/terms/v1.0',
    'Versión inicial de Términos de Servicio',
    1,
    1,
    'ACTIVE',
    '2025-01-15 00:00:00',
    NOW(),
    NOW(),
    'system',
    1
);

-- Insertar Política de Privacidad v1.0
INSERT INTO TermsVersion (
    id,
    version_number,
    type,
    title,
    content_text,
    content_url,
    change_summary,
    is_major_change,
    requires_reacceptance,
    status,
    effective_date,
    created_at,
    published_at,
    created_by,
    active
) VALUES (
    UNHEX(REPLACE('22222222-2222-2222-2222-222222222222', '-', '')),
    'v1.0_2025-01-15',
    'PRIVACY_POLICY',
    'Flowlite - Política de Privacidad',
    'POLÍTICA DE PRIVACIDAD - FLOWLITE PERSONAL FINANCE

1. INFORMACIÓN QUE RECOPILAMOS

1.1 Información Personal
- Nombre completo
- Número de identificación
- Correo electrónico
- Número de teléfono
- Dirección
- Fecha de nacimiento

1.2 Información Financiera
- Transacciones financieras
- Categorías de gastos
- Montos y fechas
- Descripciones de transacciones

1.3 Información Técnica
- Dirección IP
- Tipo de navegador
- Sistema operativo
- Información del dispositivo

2. CÓMO USAMOS SU INFORMACIÓN

Utilizamos su información para:
- Proporcionar y mejorar nuestros servicios
- Procesar transacciones
- Enviar notificaciones importantes
- Generar análisis y reportes personalizados
- Cumplir con obligaciones legales
- Prevenir fraude y mejorar seguridad

3. COMPARTIR INFORMACIÓN

NO compartimos su información personal con terceros, excepto:
- Con su consentimiento explícito
- Para cumplir con obligaciones legales
- Para proteger nuestros derechos legales
- Con proveedores de servicios bajo acuerdos de confidencialidad

4. SEGURIDAD DE DATOS

Implementamos medidas de seguridad:
- Cifrado de datos en tránsito y reposo
- Autenticación de dos factores
- Auditorías de seguridad regulares
- Control de acceso basado en roles
- Respaldo regular de datos

5. SUS DERECHOS

Usted tiene derecho a:
- Acceder a su información personal
- Corregir datos inexactos
- Solicitar eliminación de sus datos
- Exportar sus datos
- Oponerse al procesamiento
- Retirar consentimiento

6. RETENCIÓN DE DATOS

Conservamos su información mientras:
- Su cuenta esté activa
- Sea necesario para proporcionar servicios
- Lo requiera la ley (generalmente 5 años)

7. COOKIES Y TECNOLOGÍAS SIMILARES

Utilizamos cookies para:
- Mantener su sesión activa
- Recordar preferencias
- Analizar uso de la aplicación
- Mejorar experiencia del usuario

8. CAMBIOS A ESTA POLÍTICA

Le notificaremos sobre cambios importantes:
- Por correo electrónico
- Mediante notificación en la aplicación
- Requiriendo nueva aceptación si es necesario

9. TRANSFERENCIAS INTERNACIONALES

Sus datos se almacenan en servidores ubicados en Colombia.

10. MENORES DE EDAD

Nuestro servicio no está dirigido a menores de 18 años.

11. CONTACTO

Para preguntas sobre privacidad:
- Email: privacy@flowlite.com
- Teléfono: +57 (1) 234-5678

12. AUTORIDAD DE PROTECCIÓN DE DATOS

Superintendencia de Industria y Comercio (Colombia)
- www.sic.gov.co
- protecciondedatos@sic.gov.co

Fecha de vigencia: 15 de Enero de 2025
Última actualización: 15 de Enero de 2025',
    'https://flowlite.com/privacy/v1.0',
    'Versión inicial de Política de Privacidad',
    1,
    1,
    'ACTIVE',
    '2025-01-15 00:00:00',
    NOW(),
    NOW(),
    'system',
    1
);

-- Verificar inserción
SELECT
    version_number,
    type,
    title,
    status,
    effective_date,
    created_at
FROM TermsVersion
ORDER BY created_at DESC;

-- Mostrar mensaje de confirmación
SELECT 'Seed de Términos completado exitosamente' AS mensaje;
