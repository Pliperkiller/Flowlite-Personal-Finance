package com.flowlite.identifyservice.infrastructure.persistence.redis;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.flowlite.identifyservice.domain.entities.VerificationCode;
import com.flowlite.identifyservice.domain.repositories.VerificationCodeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.util.Optional;

/**
 * Implementación del repositorio de códigos de verificación usando Redis
 */
@Repository
@RequiredArgsConstructor
@Slf4j
public class RedisVerificationCodeRepository implements VerificationCodeRepository {
    
    private final RedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper;
    
    private static final String CODE_PREFIX = "verification_code:";
    private static final String EMAIL_CODE_PREFIX = "email_code:";
    private static final String TOKEN_CODE_PREFIX = "token_code:";
    
    @Override
    public void save(VerificationCode verificationCode, long ttlSeconds) {
        try {
            String codeJson = objectMapper.writeValueAsString(verificationCode);
            String codeKey = CODE_PREFIX + verificationCode.getEmail() + ":" + verificationCode.getCode();
            String emailCodeKey = EMAIL_CODE_PREFIX + verificationCode.getEmail();
            String tokenCodeKey = TOKEN_CODE_PREFIX + verificationCode.getToken();
            
            // Guardar el código con TTL
            redisTemplate.opsForValue().set(codeKey, codeJson, Duration.ofSeconds(ttlSeconds));
            redisTemplate.opsForValue().set(emailCodeKey, verificationCode.getCode(), Duration.ofSeconds(ttlSeconds));
            redisTemplate.opsForValue().set(tokenCodeKey, codeJson, Duration.ofSeconds(ttlSeconds));
            
            log.debug("Código de verificación guardado en Redis: {} para email: {}", 
                     verificationCode.getCode(), verificationCode.getEmail());
            
        } catch (JsonProcessingException e) {
            log.error("Error serializando código de verificación: {}", e.getMessage());
            throw new RuntimeException("Error guardando código de verificación", e);
        }
    }
    
    @Override
    public Optional<VerificationCode> findByEmailAndCode(String email, String code) {
        try {
            String codeKey = CODE_PREFIX + email + ":" + code;
            String codeJson = redisTemplate.opsForValue().get(codeKey);
            
            if (codeJson == null) {
                return Optional.empty();
            }
            
            VerificationCode verificationCode = objectMapper.readValue(codeJson, VerificationCode.class);
            return Optional.of(verificationCode);
            
        } catch (JsonProcessingException e) {
            log.error("Error deserializando código de verificación: {}", e.getMessage());
            return Optional.empty();
        }
    }
    
    @Override
    public Optional<VerificationCode> findByToken(String token) {
        try {
            String tokenCodeKey = TOKEN_CODE_PREFIX + token;
            log.debug("Buscando token en Redis con clave: {}", tokenCodeKey);
            
            String codeJson = redisTemplate.opsForValue().get(tokenCodeKey);
            log.debug("Valor obtenido de Redis: {}", codeJson);
            
            if (codeJson == null) {
                log.debug("No se encontró código para token: {}", token);
                return Optional.empty();
            }
            
            VerificationCode verificationCode = objectMapper.readValue(codeJson, VerificationCode.class);
            log.debug("Código deserializado exitosamente: {}", verificationCode.getCode());
            return Optional.of(verificationCode);
            
        } catch (JsonProcessingException e) {
            log.error("Error deserializando código de verificación por token: {}", e.getMessage());
            return Optional.empty();
        }
    }
    
    @Override
    public Optional<VerificationCode> findByCode(String code) {
        try {
            // Buscar en todas las claves que contengan el código
            String pattern = CODE_PREFIX + "*:" + code;
            var keys = redisTemplate.keys(pattern);
            
            if (keys == null || keys.isEmpty()) {
                return Optional.empty();
            }
            
            // Tomar la primera clave encontrada (debería ser única)
            String codeKey = keys.iterator().next();
            String codeJson = redisTemplate.opsForValue().get(codeKey);
            
            if (codeJson == null) {
                return Optional.empty();
            }
            
            VerificationCode verificationCode = objectMapper.readValue(codeJson, VerificationCode.class);
            return Optional.of(verificationCode);
            
        } catch (JsonProcessingException e) {
            log.error("Error deserializando código de verificación por código: {}", e.getMessage());
            return Optional.empty();
        }
    }
    
    @Override
    public void delete(String email, String code) {
        String codeKey = CODE_PREFIX + email + ":" + code;
        String emailCodeKey = EMAIL_CODE_PREFIX + email;
        
        // Obtener el token antes de eliminar para poder eliminar también la referencia por token
        Optional<VerificationCode> verificationCode = findByEmailAndCode(email, code);
        if (verificationCode.isPresent()) {
            String tokenCodeKey = TOKEN_CODE_PREFIX + verificationCode.get().getToken();
            redisTemplate.delete(tokenCodeKey);
        }
        
        redisTemplate.delete(codeKey);
        redisTemplate.delete(emailCodeKey);
        
        log.debug("Código de verificación eliminado: {} para email: {}", code, email);
    }
    
    @Override
    public void deleteByToken(String token) {
        Optional<VerificationCode> verificationCode = findByToken(token);
        if (verificationCode.isPresent()) {
            delete(verificationCode.get().getEmail(), verificationCode.get().getCode());
        }
    }
    
    @Override
    public boolean existsActiveCodeForEmail(String email) {
        String emailCodeKey = EMAIL_CODE_PREFIX + email;
        return redisTemplate.hasKey(emailCodeKey);
    }
    
    @Override
    public Optional<String> findActiveCodeForEmail(String email) {
        String emailCodeKey = EMAIL_CODE_PREFIX + email;
        String code = redisTemplate.opsForValue().get(emailCodeKey);
        return Optional.ofNullable(code);
    }
}
