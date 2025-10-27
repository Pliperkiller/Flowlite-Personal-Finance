package com.flowlite.identifyservice.application.ports;

/**
 * Interfaz para el servicio de envío de emails.
 * Define el contrato que deben implementar las diferentes estrategias de envío.
 */
public interface EmailService {
    
    /**
     * Envía un email de verificación al usuario
     * @param email Email del usuario
     * @param verificationToken Token de verificación
     */
    void sendVerificationEmail(String email, String verificationToken);
    
    /**
     * Envía un email de bienvenida al usuario
     * @param email Email del usuario
     * @param username Nombre de usuario
     */
    void sendWelcomeEmail(String email, String username);
}

