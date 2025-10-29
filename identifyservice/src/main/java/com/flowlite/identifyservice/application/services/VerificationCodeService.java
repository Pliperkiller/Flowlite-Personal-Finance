package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.VerificationCode;
import com.flowlite.identifyservice.domain.repositories.VerificationCodeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Servicio para gestión de códigos de verificación de 6 dígitos
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class VerificationCodeService {
    
    private final VerificationCodeRepository verificationCodeRepository;
    
    @Value("${app.verification-code.expiration-minutes:10}")
    private int expirationMinutes;
    
    @Value("${app.verification-code.max-attempts:3}")
    private int maxAttempts;
    
    private static final SecureRandom RANDOM = new SecureRandom();
    
    /**
     * Genera un código de verificación de 6 dígitos para un email
     * @param email Email del usuario
     * @return Token asociado al código
     */
    public String generateVerificationCode(String email) {
        log.info("Generando código de verificación para email: {}", email);
        
        // Generar código de 6 dígitos
        String code = generateSixDigitCode();
        
        // Generar token único
        String token = UUID.randomUUID().toString();
        
        // Crear entidad de código de verificación
        VerificationCode verificationCode = VerificationCode.builder()
                .id(UUID.randomUUID())
                .code(code)
                .email(email)
                .token(token)
                .createdAt(LocalDateTime.now())
                .expiresAt(LocalDateTime.now().plusMinutes(expirationMinutes))
                .used(false)
                .attempts(0)
                .build();
        
        // Guardar en Redis con TTL
        long ttlSeconds = expirationMinutes * 60L;
        verificationCodeRepository.save(verificationCode, ttlSeconds);
        
        log.info("Código de verificación generado exitosamente para email: {} - Código: {}", email, code);
        
        return token;
    }
    
    /**
     * Genera un código de verificación y devuelve tanto el token como el código
     * @param email Email del usuario
     * @return Map con token y código
     */
    public Map<String, String> generateVerificationCodeWithCode(String email) {
        log.info("Generando código de verificación para email: {}", email);
        
        // Generar código de 6 dígitos
        String code = generateSixDigitCode();
        
        // Generar token único
        String token = UUID.randomUUID().toString();
        
        // Crear entidad de código de verificación
        VerificationCode verificationCode = VerificationCode.builder()
                .id(UUID.randomUUID())
                .code(code)
                .email(email)
                .token(token)
                .createdAt(LocalDateTime.now())
                .expiresAt(LocalDateTime.now().plusMinutes(expirationMinutes))
                .used(false)
                .attempts(0)
                .build();
        
        // Guardar en Redis con TTL
        long ttlSeconds = expirationMinutes * 60L;
        verificationCodeRepository.save(verificationCode, ttlSeconds);
        
        log.info("Código de verificación generado exitosamente para email: {} - Código: {} - Token: {}", email, code, token);
        
        return Map.of("token", token, "code", code);
    }
    
    /**
     * Verifica un código de verificación
     * @param code Código de 6 dígitos
     * @param token Token asociado al código
     * @return Resultado de la verificación
     */
    public Map<String, Object> verifyCode(String code, String token) {
        log.info("Verificando código: {} con token: {}", code, token);
        
        try {
            // Buscar código por token
            var verificationCodeOpt = verificationCodeRepository.findByToken(token);
            
            if (verificationCodeOpt.isEmpty()) {
                log.warn("Token no encontrado: {}", token);
                return Map.of(
                    "valid", false,
                    "message", "Token inválido o expirado"
                );
            }
            
            VerificationCode verificationCode = verificationCodeOpt.get();
            
            // Verificar si el código ha expirado
            if (verificationCode.isExpired()) {
                log.warn("Código expirado para token: {}", token);
                verificationCodeRepository.deleteByToken(token);
                return Map.of(
                    "valid", false,
                    "message", "El código ha expirado"
                );
            }
            
            // Verificar si el código ya fue usado
            if (verificationCode.isUsed()) {
                log.warn("Código ya usado para token: {}", token);
                return Map.of(
                    "valid", false,
                    "message", "El código ya fue utilizado"
                );
            }
            
            // Verificar si se excedieron los intentos
            if (verificationCode.hasExceededMaxAttempts(maxAttempts)) {
                log.warn("Máximo de intentos excedido para token: {}", token);
                verificationCodeRepository.deleteByToken(token);
                return Map.of(
                    "valid", false,
                    "message", "Se excedió el número máximo de intentos"
                );
            }
            
            // Incrementar intentos
            verificationCode.incrementAttempts();
            
            // Verificar si el código coincide
            if (!verificationCode.getCode().equals(code)) {
                log.warn("Código incorrecto para token: {}", token);
                
                // Guardar intento fallido
                long ttlSeconds = expirationMinutes * 60L;
                verificationCodeRepository.save(verificationCode, ttlSeconds);
                
                return Map.of(
                    "valid", false,
                    "message", "Código incorrecto",
                    "remainingAttempts", maxAttempts - verificationCode.getAttempts()
                );
            }
            
            // Código correcto - marcar como usado
            verificationCode.markAsUsed();
            long ttlSeconds = expirationMinutes * 60L;
            verificationCodeRepository.save(verificationCode, ttlSeconds);
            
            log.info("Código verificado exitosamente para email: {}", verificationCode.getEmail());
            
            return Map.of(
                "valid", true,
                "message", "Código verificado exitosamente",
                "email", verificationCode.getEmail(),
                "token", token
            );
            
        } catch (Exception e) {
            log.error("Error verificando código: {}", e.getMessage(), e);
            return Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            );
        }
    }
    
    /**
     * Obtiene un código de verificación por token
     * @param token Token asociado al código
     * @return Código de verificación si existe
     */
    public Optional<VerificationCode> getVerificationCodeByToken(String token) {
        return verificationCodeRepository.findByToken(token);
    }
    
    /**
     * Obtiene el código activo para un email
     * @param email Email del usuario
     * @return Código de verificación activo si existe
     */
    public Optional<VerificationCode> getVerificationCodeByEmail(String email) {
        var activeCodeOpt = verificationCodeRepository.findActiveCodeForEmail(email);
        if (activeCodeOpt.isPresent()) {
            String code = activeCodeOpt.get();
            return verificationCodeRepository.findByEmailAndCode(email, code);
        }
        return Optional.empty();
    }
    
    /**
     * Busca un código de verificación por el código de 6 dígitos
     * @param code Código de 6 dígitos
     * @return Código de verificación si existe
     */
    public Optional<VerificationCode> getVerificationCodeByCode(String code) {
        return verificationCodeRepository.findByCode(code);
    }
    
    /**
     * Verifica un código de verificación solo con el código de 6 dígitos
     * @param code Código de 6 dígitos
     * @return Resultado de la verificación
     */
    public Map<String, Object> verifyCodeByCodeOnly(String code) {
        log.info("Verificando código: {}", code);
        
        try {
            // Buscar código por el código de 6 dígitos
            var verificationCodeOpt = verificationCodeRepository.findByCode(code);
            
            if (verificationCodeOpt.isEmpty()) {
                log.warn("Código no encontrado: {}", code);
                return Map.of(
                    "valid", false,
                    "message", "Código inválido o expirado"
                );
            }
            
            VerificationCode verificationCode = verificationCodeOpt.get();
            
            // Verificar si el código ha expirado
            if (verificationCode.isExpired()) {
                log.warn("Código expirado: {}", code);
                verificationCodeRepository.deleteByToken(verificationCode.getToken());
                return Map.of(
                    "valid", false,
                    "message", "El código ha expirado"
                );
            }
            
            // Verificar si el código ya fue usado
            if (verificationCode.isUsed()) {
                log.warn("Código ya usado: {}", code);
                return Map.of(
                    "valid", false,
                    "message", "El código ya fue utilizado"
                );
            }
            
            // Verificar si se excedieron los intentos
            if (verificationCode.hasExceededMaxAttempts(maxAttempts)) {
                log.warn("Máximo de intentos excedido para código: {}", code);
                verificationCodeRepository.deleteByToken(verificationCode.getToken());
                return Map.of(
                    "valid", false,
                    "message", "Se excedió el número máximo de intentos"
                );
            }
            
            // Incrementar intentos
            verificationCode.incrementAttempts();
            
            // Código correcto - marcar como usado
            verificationCode.markAsUsed();
            long ttlSeconds = expirationMinutes * 60L;
            verificationCodeRepository.save(verificationCode, ttlSeconds);
            
            log.info("Código verificado exitosamente para email: {}", verificationCode.getEmail());
            
            return Map.of(
                "valid", true,
                "message", "Código verificado exitosamente",
                "email", verificationCode.getEmail(),
                "token", verificationCode.getToken()
            );
            
        } catch (Exception e) {
            log.error("Error verificando código: {}", e.getMessage(), e);
            return Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            );
        }
    }
    
    /**
     * Verifica un código de verificación con código y email para mayor seguridad
     * @param code Código de 6 dígitos
     * @param email Email del usuario
     * @return Resultado de la verificación
     */
    public Map<String, Object> verifyCodeWithEmail(String code, String email) {
        log.info("Verificando código: {} para email: {}", code, email);
        
        try {
            // Buscar código por email y código (más seguro)
            var verificationCodeOpt = verificationCodeRepository.findByEmailAndCode(email, code);
            
            if (verificationCodeOpt.isEmpty()) {
                log.warn("Código no encontrado para email: {} con código: {}", email, code);
                return Map.of(
                    "valid", false,
                    "message", "Código inválido o expirado"
                );
            }
            
            VerificationCode verificationCode = verificationCodeOpt.get();
            
            // Verificar si el código ha expirado
            if (verificationCode.isExpired()) {
                log.warn("Código expirado para email: {}", email);
                verificationCodeRepository.deleteByToken(verificationCode.getToken());
                return Map.of(
                    "valid", false,
                    "message", "El código ha expirado"
                );
            }
            
            // Verificar si el código ya fue usado
            if (verificationCode.isUsed()) {
                log.warn("Código ya usado para email: {}", email);
                return Map.of(
                    "valid", false,
                    "message", "El código ya fue utilizado"
                );
            }
            
            // Verificar si se excedieron los intentos
            if (verificationCode.hasExceededMaxAttempts(maxAttempts)) {
                log.warn("Máximo de intentos excedido para email: {}", email);
                verificationCodeRepository.deleteByToken(verificationCode.getToken());
                return Map.of(
                    "valid", false,
                    "message", "Se excedió el número máximo de intentos"
                );
            }
            
            // Incrementar intentos
            verificationCode.incrementAttempts();
            
            // Código correcto - marcar como usado
            verificationCode.markAsUsed();
            long ttlSeconds = expirationMinutes * 60L;
            verificationCodeRepository.save(verificationCode, ttlSeconds);
            
            log.info("Código verificado exitosamente para email: {}", email);
            
            return Map.of(
                "valid", true,
                "message", "Código verificado exitosamente",
                "email", email,
                "token", verificationCode.getToken()
            );
            
        } catch (Exception e) {
            log.error("Error verificando código para email {}: {}", email, e.getMessage(), e);
            return Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            );
        }
    }
    
    /**
     * Revoca el código activo para un email específico
     * @param email Email del usuario
     */
    public void revokeActiveCodeForEmail(String email) {
        log.info("Revocando código activo para email: {}", email);
        
        try {
            // Buscar si existe un código activo para este email
            if (verificationCodeRepository.existsActiveCodeForEmail(email)) {
                // Obtener el código activo
                var activeCodeOpt = verificationCodeRepository.findByEmailAndCode(email, 
                    verificationCodeRepository.findActiveCodeForEmail(email).orElse(""));
                
                if (activeCodeOpt.isPresent()) {
                    VerificationCode activeCode = activeCodeOpt.get();
                    // Eliminar el código activo
                    verificationCodeRepository.deleteByToken(activeCode.getToken());
                    log.info("Código activo revocado para email: {}", email);
                }
            }
        } catch (Exception e) {
            log.warn("No se pudo revocar código activo para email: {} - {}", email, e.getMessage());
            // No lanzar excepción, continuar con la generación del nuevo código
        }
    }
    
    /**
     * Obtiene los minutos de expiración configurados
     * @return Minutos de expiración
     */
    public int getExpirationMinutes() {
        return expirationMinutes;
    }
    
    /**
     * Genera un código de 6 dígitos aleatorio
     */
    private String generateSixDigitCode() {
        int code = RANDOM.nextInt(900000) + 100000; // Rango: 100000-999999
        return String.valueOf(code);
    }
}
