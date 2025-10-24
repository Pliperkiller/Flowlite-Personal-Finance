package com.flowlite.identifyservice.infrastructure.services;

import com.flowlite.identifyservice.application.ports.EmailService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.MailSender;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import jakarta.mail.internet.MimeMessage;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailServiceImpl implements EmailService {
    
    private final MailSender mailSender;
    private final JavaMailSender javaMailSender;
    private final TemplateEngine templateEngine;
    
    @Value("${app.email.from:noreply@flowlite.com}")
    private String fromEmail;
    
    @Value("${app.email.verification-url:http://localhost:8080/auth/verify}")
    private String verificationBaseUrl;
    
    @Override
    public void sendVerificationEmail(String email, String verificationToken) {
        try {
            String verificationUrl = verificationBaseUrl + "?token=" + verificationToken;
            
            // Para desarrollo: loguear en consola y también enviar a MailHog
            log.info("=== EMAIL DE VERIFICACIÓN (MODO DESARROLLO) ===");
            log.info("Para: {}", email);
            log.info("Token: {}", verificationToken);
            log.info("URL de verificación: {}", verificationUrl);
            log.info("=============================================");
            
            // También intentar enviar a MailHog en desarrollo usando plantilla HTML
            try {
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
                log.info("Email HTML enviado a MailHog para: {}", email);
                
            } catch (Exception e) {
                log.warn("No se pudo enviar email HTML a MailHog: {}", e.getMessage());
            }
            
            return;
            
        } catch (Exception e) {
            log.error("Error enviando email de verificación a {}: {}", email, e.getMessage());
            throw new RuntimeException("Error enviando email de verificación", e);
        }
    }
    
    @Override
    public void sendWelcomeEmail(String email, String username) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo(email);
            message.setSubject("¡Bienvenido a Flowlite!");
            
            String emailBody = String.format("""
                ¡Hola %s!
                
                ¡Tu cuenta ha sido verificada exitosamente!
                
                Ya puedes iniciar sesión en Flowlite y comenzar a gestionar tus finanzas personales.
                
                ¡Gracias por unirte a nuestra comunidad!
                
                El equipo de Flowlite
                """, username);
            
            message.setText(emailBody);
            
            mailSender.send(message);
            log.info("Email de bienvenida enviado a: {}", email);
            
        } catch (Exception e) {
            log.error("Error enviando email de bienvenida a {}: {}", email, e.getMessage());
            // No lanzamos excepción aquí porque el usuario ya está registrado
        }
    }
    
    private String extractUsernameFromEmail(String email) {
        if (email != null && email.contains("@")) {
            return email.substring(0, email.indexOf("@"));
        }
        return "Usuario";
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
