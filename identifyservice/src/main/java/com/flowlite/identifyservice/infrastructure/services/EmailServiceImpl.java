package com.flowlite.identifyservice.infrastructure.services;

import com.flowlite.identifyservice.application.ports.EmailService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.MailSender;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmailServiceImpl implements EmailService {
    
    private final MailSender mailSender;
    private final JavaMailSender javaMailSender;
    
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
            
            // También intentar enviar a MailHog en desarrollo
            try {
                SimpleMailMessage message = new SimpleMailMessage();
                message.setFrom(fromEmail);
                message.setTo(email);
                message.setSubject("Verifica tu cuenta en Flowlite");
                
                String emailBody = String.format("""
                    ¡Hola!
                    
                    Gracias por registrarte en Flowlite. Para completar tu registro, 
                    por favor verifica tu cuenta haciendo clic en el siguiente enlace:
                    
                    %s
                    
                    Este enlace será válido por 24 horas.
                    
                    Si no solicitaste este registro, puedes ignorar este email.
                    
                    ¡Bienvenido a Flowlite!
                    
                    El equipo de Flowlite
                    """, verificationUrl);
                
                message.setText(emailBody);
                
                // Usar JavaMailSender directamente para MailHog
                javaMailSender.send(message);
                log.info("Email enviado a MailHog para: {}", email);
                
            } catch (Exception e) {
                log.warn("No se pudo enviar email a MailHog: {}", e.getMessage());
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
}
