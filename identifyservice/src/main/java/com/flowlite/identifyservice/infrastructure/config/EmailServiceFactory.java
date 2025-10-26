package com.flowlite.identifyservice.infrastructure.config;

import com.flowlite.identifyservice.application.ports.EmailService;
import com.flowlite.identifyservice.infrastructure.services.EmailServiceMailHog;
import com.flowlite.identifyservice.infrastructure.services.EmailServiceMailerSend;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

/**
 * Factory para seleccionar la implementación de EmailService según la configuración.
 * Implementa el patrón Strategy para permitir cambiar entre diferentes proveedores de email.
 */
@Slf4j
@Configuration
@RequiredArgsConstructor
public class EmailServiceFactory {
    
    @Value("${app.email.provider:mailersend}")
    private String emailProvider;
    
    private final EmailServiceMailHog emailServiceMailHog;
    private final EmailServiceMailerSend emailServiceMailerSend;
    
    /**
     * Bean principal que selecciona la implementación de EmailService según la configuración.
     * 
     * @return La implementación de EmailService configurada
     */
    @Bean
    @Primary
    public EmailService emailService() {
        log.info("Configurando EmailService con proveedor: {}", emailProvider);
        
        return switch (emailProvider.toLowerCase()) {
            case "mailhog" -> {
                log.info("Usando MailHog para desarrollo");
                yield emailServiceMailHog;
            }
            case "mailersend" -> {
                log.info("Usando MailerSend para producción");
                yield emailServiceMailerSend;
            }
            default -> {
                log.warn("Proveedor de email '{}' no reconocido, usando MailerSend por defecto", emailProvider);
                yield emailServiceMailerSend;
            }
        };
    }
}
