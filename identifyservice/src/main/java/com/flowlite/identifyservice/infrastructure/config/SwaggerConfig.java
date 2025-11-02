package com.flowlite.identifyservice.infrastructure.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SwaggerConfig {

    @Value("${server.port:8000}")
    private String serverPort;

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Identity Service - Authentication API")
                        .description("""
                            API para autenticación de usuarios con soporte para:
                            - Registro de usuarios tradicional
                            - Preregistro con verificación de email
                            - Verificación de email desde enlaces
                            - Login con credenciales
                            - Autenticación OAuth2 con Google
                            - Generación de JWT tokens
                            - Revocación de tokens con Redis
                            - Validación de tokens
                            - Gestión de información de usuarios
                            - Envío de emails con plantillas HTML
                            - Gestión de información personal de usuarios
                            - Actualización de datos personales con validaciones
                            - Recuperación de contraseñas por email (flujo tradicional)
                            - Recuperación de contraseñas con códigos de verificación (flujo moderno)
                            - Recuperación de información de usuario
                            """)
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Identity Service Team")
                                .email("support@identifyservice.com"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:" + serverPort)
                                .description("Servidor de desarrollo local"),
                        new Server()
                                .url("https://api.flowlite.com")
                                .description("Servidor de producción")
                ))
                .addSecurityItem(new SecurityRequirement()
                        .addList("Bearer Authentication"))
                .components(new Components()
                        .addSecuritySchemes("Bearer Authentication", 
                                new SecurityScheme()
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")
                                        .description("JWT token obtenido de los endpoints de autenticación")));
    }
}
