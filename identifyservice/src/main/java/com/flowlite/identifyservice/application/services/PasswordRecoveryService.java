package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.repositories.UserRepository;
import com.flowlite.identifyservice.infrastructure.security.jwt.JwtTokenProvider;
import com.flowlite.identifyservice.application.ports.EmailService;
import com.flowlite.identifyservice.domain.valueobjects.Password;
import lombok.*;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import com.flowlite.identifyservice.application.ports.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Servicio para gestión de recuperación de contraseñas
 */
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Slf4j
public class PasswordRecoveryService {

    final UserRepository userRepository;
    final JwtTokenProvider tokenProvider;
    final EmailService emailService;
    final PasswordEncoder passwordEncoder;
    final TokenRevocationService tokenRevocationService;

    @Value("${app.password-recovery.expiration-hours:24}")
    int expirationHours;

    @Value("${app.password-recovery.base-url:http://localhost:8080}")
    String baseUrl;

    /**
     * Solicita recuperación de contraseña por email
     */
    @Transactional
    public Map<String, Object> requestPasswordRecovery(@NonNull String email) {
        log.info("Solicitud de recuperación de contraseña para email: {}", email);

        // Buscar usuario por email
        Optional<User> userOpt = userRepository.findByEmail(email);
        
        if (userOpt.isEmpty()) {
            log.warn("Intento de recuperación de contraseña para email no registrado: {}", email);
            // Por seguridad, no revelamos si el email existe o no
            return Map.of(
                "message", "Si el email está registrado, recibirás un enlace de recuperación",
                "status", "success"
            );
        }

        User user = userOpt.get();
        
        // Generar token de recuperación con expiración
        String recoveryToken = tokenProvider.generatePasswordRecoveryToken(user.getEmail().getValue(), expirationHours);
        
        // Crear enlace de recuperación
        String recoveryUrl = baseUrl + "/auth/reset-password?token=" + recoveryToken;
        
        // Preparar datos para el email
        Map<String, Object> emailData = new HashMap<>();
        emailData.put("username", user.getUsername().getValue());
        emailData.put("recoveryUrl", recoveryUrl);
        emailData.put("expirationHours", expirationHours);
        
        try {
            // Enviar email de recuperación
            emailService.sendPasswordRecoveryEmail(user.getEmail().getValue(), emailData);
            
            log.info("Email de recuperación enviado exitosamente a: {}", email);
            
            return Map.of(
                "message", "Si el email está registrado, recibirás un enlace de recuperación",
                "status", "success",
                "email", email,
                "expirationHours", expirationHours
            );
            
        } catch (Exception e) {
            log.error("Error al enviar email de recuperación a: {}", email, e);
            throw new RuntimeException("Error al enviar email de recuperación", e);
        }
    }

    /**
     * Resetea la contraseña usando el token de recuperación
     */
    @Transactional
    public Map<String, Object> resetPassword(@NonNull String token, @NonNull String newPassword) {
        log.info("Intento de reset de contraseña con token");

        try {
            // Verificar si el token está revocado primero
            if (tokenRevocationService.isTokenRevoked(token)) {
                throw new IllegalArgumentException("Token revocado - no puede ser usado");
            }
            
            // Validar token de recuperación
            if (!tokenProvider.isPasswordRecoveryToken(token)) {
                throw new IllegalArgumentException("Token inválido para recuperación de contraseña");
            }

            // Extraer email del token
            String email = tokenProvider.getEmailFromPasswordRecoveryToken(token);
            if (email == null) {
                throw new IllegalArgumentException("Token inválido o expirado");
            }

            // Buscar usuario por email
            Optional<User> userOpt = userRepository.findByEmail(email);
            if (userOpt.isEmpty()) {
                throw new IllegalArgumentException("Usuario no encontrado");
            }

            User user = userOpt.get();
            
            // Verificar que la nueva contraseña sea diferente a la actual
            if (user.getPassword().isPresent() && 
                passwordEncoder.matches(newPassword, user.getPassword().get().getValue())) {
                throw new IllegalArgumentException("La nueva contraseña debe ser diferente a la actual");
            }

            // Actualizar contraseña
            String encodedPassword = passwordEncoder.encode(newPassword);
            user.setPassword(new Password(encodedPassword));
            
            User updatedUser = userRepository.save(user);
            
            // Revocar el token de recuperación para que no pueda ser reutilizado
            boolean revoked = tokenRevocationService.revokeToken(token);
            if (revoked) {
                log.info("Token de recuperación revocado exitosamente");
            } else {
                log.warn("No se pudo revocar el token de recuperación");
            }
            
            log.info("Contraseña actualizada exitosamente para usuario: {}", updatedUser.getUsername());
            
            return Map.of(
                "message", "Contraseña actualizada exitosamente",
                "status", "success",
                "username", updatedUser.getUsername().getValue(),
                "email", updatedUser.getEmail().getValue()
            );
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en reset de contraseña: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error al resetear contraseña", e);
            throw new RuntimeException("Error interno al resetear contraseña", e);
        }
    }

    /**
     * Valida si un token de recuperación es válido
     */
    public Map<String, Object> validateRecoveryToken(@NonNull String token) {
        try {
            if (!tokenProvider.isPasswordRecoveryToken(token)) {
                return Map.of(
                    "valid", false,
                    "message", "Token inválido para recuperación de contraseña"
                );
            }

            String email = tokenProvider.getEmailFromPasswordRecoveryToken(token);
            if (email == null) {
                return Map.of(
                    "valid", false,
                    "message", "Token expirado o inválido"
                );
            }

            // Verificar que el usuario existe
            Optional<User> userOpt = userRepository.findByEmail(email);
            if (userOpt.isEmpty()) {
                return Map.of(
                    "valid", false,
                    "message", "Usuario no encontrado"
                );
            }

            return Map.of(
                "valid", true,
                "message", "Token válido",
                "email", email,
                "username", userOpt.get().getUsername()
            );

        } catch (Exception e) {
            log.error("Error al validar token de recuperación", e);
            return Map.of(
                "valid", false,
                "message", "Error al validar token"
            );
        }
    }

    /**
     * Obtiene información del usuario por email (para casos donde se olvida el username)
     */
    public Map<String, Object> getUserInfoByEmail(@NonNull String email) {
        log.info("Consulta de información de usuario por email: {}", email);

        Optional<User> userOpt = userRepository.findByEmail(email);
        
        if (userOpt.isEmpty()) {
            // Por seguridad, no revelamos si el email existe
            return Map.of(
                "message", "Si el email está registrado, recibirás un enlace de recuperación",
                "status", "success"
            );
        }

        User user = userOpt.get();
        
        // Enviar email con información del usuario
        Map<String, Object> emailData = new HashMap<>();
        emailData.put("username", user.getUsername().getValue());
        emailData.put("email", user.getEmail().getValue());
        
        try {
            emailService.sendUserInfoEmail(user.getEmail().getValue(), emailData);
            
            log.info("Email con información de usuario enviado a: {}", email);
            
            return Map.of(
                "message", "Si el email está registrado, recibirás un email con tu información de usuario",
                "status", "success"
            );
            
        } catch (Exception e) {
            log.error("Error al enviar email con información de usuario a: {}", email, e);
            throw new RuntimeException("Error al enviar email con información de usuario", e);
        }
    }
}
