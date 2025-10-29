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
 * Servicio para gestión de recuperación de contraseñas con códigos de verificación
 */
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Slf4j
public class PasswordRecoveryCodeService {

    final UserRepository userRepository;
    final JwtTokenProvider tokenProvider;
    final EmailService emailService;
    final PasswordEncoder passwordEncoder;
    final TokenRevocationService tokenRevocationService;
    final VerificationCodeService verificationCodeService;

    @Value("${app.password-recovery.expiration-hours:24}")
    int expirationHours;

    /**
     * Solicita código de verificación para recuperación de contraseña
     */
    @Transactional
    public Map<String, Object> requestPasswordRecoveryCode(@NonNull String email) {
        log.info("Solicitud de código de verificación para recuperación de contraseña: {}", email);

        // Buscar usuario por email
        Optional<User> userOpt = userRepository.findByEmail(email);
        
        if (userOpt.isEmpty()) {
            log.warn("Intento de recuperación de contraseña para email no registrado: {}", email);
            // Por seguridad, no revelamos si el email existe o no
            return Map.of(
                "message", "Si el email está registrado, recibirás un código de verificación",
                "status", "success"
            );
        }

        User user = userOpt.get();
        
        try {
            // Revocar código anterior si existe
            verificationCodeService.revokeActiveCodeForEmail(email);
            
            // Generar código de verificación y obtener tanto token como código directamente
            Map<String, String> codeData = verificationCodeService.generateVerificationCodeWithCode(email);
            String token = codeData.get("token");
            String verificationCode = codeData.get("code");
            
            log.info("Código generado para email: {} - Token: {} - Código: {}", email, token, verificationCode);
            
            // Preparar datos para el email
            Map<String, Object> emailData = new HashMap<>();
            emailData.put("username", user.getUsername().getValue());
            emailData.put("token", token);
            emailData.put("verificationCode", verificationCode);
            emailData.put("expirationMinutes", verificationCodeService.getExpirationMinutes());
            
            // Enviar email con código de verificación
            emailService.sendPasswordRecoveryCodeEmail(user.getEmail().getValue(), emailData);
            
            log.info("Email con código de verificación enviado exitosamente a: {}", email);
            
            return Map.of(
                "message", "Si el email está registrado, recibirás un código de verificación",
                "status", "success",
                "email", email
            );
            
        } catch (Exception e) {
            log.error("Error al enviar código de verificación a: {}", email, e);
            throw new RuntimeException("Error al enviar código de verificación", e);
        }
    }


    /**
     * Verifica el código de verificación y devuelve el token de restablecimiento
     */
    @Transactional
    public Map<String, Object> verifyCodeAndGetResetToken(@NonNull String code, @NonNull String email) {
        log.info("Verificando código de verificación: {} para email: {}", code, email);

        try {
            // Verificar el código usando código y email para mayor seguridad
            Map<String, Object> verificationResult = verificationCodeService.verifyCodeWithEmail(code, email);
            
            if (!Boolean.TRUE.equals(verificationResult.get("valid"))) {
                return Map.of(
                    "valid", false,
                    "message", verificationResult.get("message")
                );
            }
            
            // Buscar usuario por email
            Optional<User> userOpt = userRepository.findByEmail(email);
            if (userOpt.isEmpty()) {
                throw new IllegalArgumentException("Usuario no encontrado");
            }

            User user = userOpt.get();
            
            // Generar token de restablecimiento de contraseña
            String resetToken = tokenProvider.generatePasswordRecoveryToken(email, expirationHours);
            
            log.info("Código verificado exitosamente para email: {}, token de restablecimiento generado", email);
            
            return Map.of(
                "valid", true,
                "message", "Código verificado exitosamente",
                "resetToken", resetToken,
                "email", email,
                "username", user.getUsername().getValue()
            );
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en verificación de código: {}", e.getMessage());
            return Map.of(
                "valid", false,
                "message", e.getMessage()
            );
        } catch (Exception e) {
            log.error("Error al verificar código de verificación", e);
            return Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            );
        }
    }

    /**
     * Resetea la contraseña usando el token de restablecimiento
     */
    @Transactional
    public Map<String, Object> resetPassword(@NonNull String resetToken, @NonNull String newPassword) {
        log.info("Intento de reset de contraseña con token de restablecimiento");

        try {
            // Verificar si el token está revocado primero
            if (tokenRevocationService.isTokenRevoked(resetToken)) {
                throw new IllegalArgumentException("Token revocado - no puede ser usado");
            }
            
            // Validar token de recuperación
            if (!tokenProvider.isPasswordRecoveryToken(resetToken)) {
                throw new IllegalArgumentException("Token inválido para recuperación de contraseña");
            }

            // Extraer email del token
            String email = tokenProvider.getEmailFromPasswordRecoveryToken(resetToken);
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
            boolean revoked = tokenRevocationService.revokeToken(resetToken);
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
}
