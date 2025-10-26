package com.flowlite.identifyservice.infrastructure.services;

import com.flowlite.identifyservice.application.ports.EmailService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;

import jakarta.mail.internet.MimeMessage;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/**
 * Implementación del servicio de email para MailerSend (producción).
 * Utiliza MailerSend como proveedor de email transaccional para producción.
 */
@Slf4j
@Service("emailServiceMailerSend")
@RequiredArgsConstructor
public class EmailServiceMailerSend implements EmailService {
    
    private final JavaMailSender javaMailSender;
    
    @Value("${app.email.from:MS_p2qoC5@test-y7zpl98wwzp45vx6.mlsender.net}")
    private String fromEmail;
    
    @Value("${app.email.verification-url:http://localhost:8080/auth/verify}")
    private String verificationBaseUrl;
    
    @Override
    public void sendVerificationEmail(String email, String verificationToken) {
        try {
            String verificationUrl = verificationBaseUrl + "?token=" + verificationToken;
            
            log.info("=== ENVIANDO EMAIL DE VERIFICACIÓN (MAILERSEND) ===");
            log.info("Para: {}", email);
            log.info("Token: {}", verificationToken);
            log.info("URL de verificación: {}", verificationUrl);
            log.info("=============================================");
            
            // Leer plantilla HTML y reemplazar variables
            String htmlContent = getVerificationEmailTemplate(verificationUrl);
            
            // Crear mensaje HTML
            MimeMessage message = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(fromEmail);
            helper.setTo(email);
            helper.setSubject("Verifica tu cuenta en Flowlite");
            helper.setText(htmlContent, true); // true = HTML
            
            javaMailSender.send(message);
            log.info("Email HTML enviado exitosamente a MailerSend para: {}", email);
            
        } catch (Exception e) {
            log.error("Error enviando email de verificación a {}: {}", email, e.getMessage());
            throw new RuntimeException("Error enviando email de verificación", e);
        }
    }
    
    @Override
    public void sendWelcomeEmail(String email, String username) {
        try {
            String emailBody = String.format("""
                ¡Hola %s!
                
                ¡Tu cuenta ha sido verificada exitosamente!
                
                Ya puedes iniciar sesión en Flowlite y comenzar a gestionar tus finanzas personales.
                
                ¡Gracias por unirte a nuestra comunidad!
                
                El equipo de Flowlite
                """, username);
            
            // Crear mensaje simple
            MimeMessage message = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(fromEmail);
            helper.setTo(email);
            helper.setSubject("¡Bienvenido a Flowlite!");
            helper.setText(emailBody, false); // false = texto plano
            
            javaMailSender.send(message);
            log.info("Email de bienvenida enviado a MailerSend para: {}", email);
            
        } catch (Exception e) {
            log.error("Error enviando email de bienvenida a {}: {}", email, e.getMessage());
            // No lanzamos excepción aquí porque el usuario ya está registrado
        }
    }
    
    @Override
    public void sendPasswordRecoveryEmail(String email, java.util.Map<String, Object> data) {
        try {
            String username = (String) data.get("username");
            String recoveryUrl = (String) data.get("recoveryUrl");
            Integer expirationHours = (Integer) data.get("expirationHours");
            
            log.info("=== ENVIANDO EMAIL DE RECUPERACIÓN DE CONTRASEÑA (MAILERSEND) ===");
            log.info("Para: {}", email);
            log.info("Usuario: {}", username);
            log.info("URL de recuperación: {}", recoveryUrl);
            log.info("Expira en: {} horas", expirationHours);
            log.info("=============================================================");
            
            // Leer plantilla HTML y reemplazar variables
            String htmlContent = getPasswordRecoveryEmailTemplate(username, recoveryUrl, expirationHours);
            
            // Crear mensaje HTML
            MimeMessage message = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(fromEmail);
            helper.setTo(email);
            helper.setSubject("Recupera tu contraseña en Flowlite");
            helper.setText(htmlContent, true); // true = HTML
            
            javaMailSender.send(message);
            log.info("Email de recuperación de contraseña enviado exitosamente a MailerSend para: {}", email);
            
        } catch (Exception e) {
            log.error("Error enviando email de recuperación de contraseña a {}: {}", email, e.getMessage());
            throw new RuntimeException("Error enviando email de recuperación de contraseña", e);
        }
    }
    
    @Override
    public void sendUserInfoEmail(String email, java.util.Map<String, Object> data) {
        try {
            String username = (String) data.get("username");
            String userEmail = (String) data.get("email");
            
            log.info("=== ENVIANDO EMAIL CON INFORMACIÓN DE USUARIO (MAILERSEND) ===");
            log.info("Para: {}", email);
            log.info("Usuario: {}", username);
            log.info("Email del usuario: {}", userEmail);
            log.info("=========================================================");
            
            // Leer plantilla HTML y reemplazar variables
            String htmlContent = getUserInfoEmailTemplate(username, userEmail);
            
            // Crear mensaje HTML
            MimeMessage message = javaMailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            helper.setFrom(fromEmail);
            helper.setTo(email);
            helper.setSubject("Información de tu cuenta en Flowlite");
            helper.setText(htmlContent, true); // true = HTML
            
            javaMailSender.send(message);
            log.info("Email con información de usuario enviado exitosamente a MailerSend para: {}", email);
            
        } catch (Exception e) {
            log.error("Error enviando email con información de usuario a {}: {}", email, e.getMessage());
            throw new RuntimeException("Error enviando email con información de usuario", e);
        }
    }
    
    private String getVerificationEmailTemplate(String verificationUrl) {
        try {
            // Leer el archivo HTML de la plantilla
            InputStream inputStream = getClass().getClassLoader().getResourceAsStream("templates/email/verification.html");
            if (inputStream == null) {
                throw new RuntimeException("No se pudo encontrar la plantilla verification.html");
            }
            
            String htmlTemplate = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
            inputStream.close();
            
            // Reemplazar {verificationUrl} con la URL real
            return htmlTemplate.replace("{verificationUrl}", verificationUrl);
            
        } catch (Exception e) {
            log.error("Error leyendo plantilla HTML: {}", e.getMessage());
            throw new RuntimeException("Error procesando plantilla de email", e);
        }
    }
    
    private String getPasswordRecoveryEmailTemplate(String username, String recoveryUrl, Integer expirationHours) {
        try {
            // Leer el archivo HTML de la plantilla
            InputStream inputStream = getClass().getClassLoader().getResourceAsStream("templates/email/password-recovery.html");
            if (inputStream == null) {
                throw new RuntimeException("No se pudo encontrar la plantilla password-recovery.html");
            }
            
            String htmlTemplate = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
            inputStream.close();
            
            // Reemplazar variables
            return htmlTemplate
                .replace("{username}", username != null ? username : "Usuario")
                .replace("{recoveryUrl}", recoveryUrl)
                .replace("{expirationHours}", expirationHours != null ? expirationHours.toString() : "24");
            
        } catch (Exception e) {
            log.error("Error leyendo plantilla HTML de recuperación: {}", e.getMessage());
            throw new RuntimeException("Error procesando plantilla de email de recuperación", e);
        }
    }
    
    private String getUserInfoEmailTemplate(String username, String userEmail) {
        try {
            // Leer el archivo HTML de la plantilla
            InputStream inputStream = getClass().getClassLoader().getResourceAsStream("templates/email/user-info.html");
            if (inputStream == null) {
                throw new RuntimeException("No se pudo encontrar la plantilla user-info.html");
            }
            
            String htmlTemplate = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
            inputStream.close();
            
            // Reemplazar variables
            return htmlTemplate
                .replace("{username}", username != null ? username : "Usuario")
                .replace("{email}", userEmail != null ? userEmail : "usuario@example.com");
            
        } catch (Exception e) {
            log.error("Error leyendo plantilla HTML de información de usuario: {}", e.getMessage());
            throw new RuntimeException("Error procesando plantilla de email de información de usuario", e);
        }
    }
}
