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
}
