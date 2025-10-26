package com.flowlite.identifyservice.application.ports;

import java.util.Map;

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
    
    /**
     * Envía un email de recuperación de contraseña al usuario
     * @param email Email del usuario
     * @param data Datos para el email (username, recoveryUrl, expirationHours)
     */
    void sendPasswordRecoveryEmail(String email, Map<String, Object> data);
    
    /**
     * Envía un email con información del usuario (username, email)
     * @param email Email del usuario
     * @param data Datos del usuario (username, email)
     */
    void sendUserInfoEmail(String email, Map<String, Object> data);
}

