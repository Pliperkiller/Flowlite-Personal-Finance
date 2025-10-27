package com.flowlite.identifyservice.infrastructure.persistence.redis;

import com.flowlite.identifyservice.domain.entities.PendingUserData;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;

@Repository
@RequiredArgsConstructor
public class PendingUserRedisRepository {
    
    private final RedisTemplate<String, Object> redisTemplate;
    
    private static final String PENDING_USER_PREFIX = "pending_user:";
    private static final String EMAIL_INDEX_PREFIX = "pending_email:";
    private static final String USERNAME_INDEX_PREFIX = "pending_username:";
    private static final String TOKEN_INDEX_PREFIX = "pending_token:";
    
    // TTL por defecto: 24 horas
    private static final long DEFAULT_TTL_HOURS = 24;
    
    public void save(PendingUserData pendingUser) {
        String key = PENDING_USER_PREFIX + pendingUser.getVerificationToken();
        
        // Guardar datos del usuario pendiente como Map para evitar problemas de serialización
        Map<String, Object> userData = new HashMap<>();
        userData.put("username", pendingUser.getUsername());
        userData.put("email", pendingUser.getEmail());
        userData.put("password", pendingUser.getPassword());
        userData.put("verificationToken", pendingUser.getVerificationToken());
        userData.put("createdAt", pendingUser.getCreatedAt().toString());
        userData.put("tokenExpiration", pendingUser.getTokenExpiration().toString());
        userData.put("isVerified", pendingUser.getIsVerified());
        
        redisTemplate.opsForValue().set(key, userData, Duration.ofHours(DEFAULT_TTL_HOURS));
        
        // Crear índices para búsquedas rápidas
        String emailKey = EMAIL_INDEX_PREFIX + pendingUser.getEmail();
        String usernameKey = USERNAME_INDEX_PREFIX + pendingUser.getUsername();
        String tokenKey = TOKEN_INDEX_PREFIX + pendingUser.getVerificationToken();
        
        // Los índices apuntan al token principal
        redisTemplate.opsForValue().set(emailKey, pendingUser.getVerificationToken(), Duration.ofHours(DEFAULT_TTL_HOURS));
        redisTemplate.opsForValue().set(usernameKey, pendingUser.getVerificationToken(), Duration.ofHours(DEFAULT_TTL_HOURS));
        redisTemplate.opsForValue().set(tokenKey, pendingUser.getVerificationToken(), Duration.ofHours(DEFAULT_TTL_HOURS));
    }
    
    public Optional<PendingUserData> findByToken(String token) {
        String key = PENDING_USER_PREFIX + token;
        Object data = redisTemplate.opsForValue().get(key);
        
        if (data instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> userData = (Map<String, Object>) data;
            
            PendingUserData pendingUser = PendingUserData.builder()
                .username((String) userData.get("username"))
                .email((String) userData.get("email"))
                .password((String) userData.get("password"))
                .verificationToken((String) userData.get("verificationToken"))
                .createdAt(LocalDateTime.parse((String) userData.get("createdAt")))
                .tokenExpiration(LocalDateTime.parse((String) userData.get("tokenExpiration")))
                .isVerified((Boolean) userData.get("isVerified"))
                .build();
            
            return Optional.of(pendingUser);
        }
        return Optional.empty();
    }
    
    public Optional<PendingUserData> findByEmail(String email) {
        String emailKey = EMAIL_INDEX_PREFIX + email;
        Object tokenObj = redisTemplate.opsForValue().get(emailKey);
        
        if (tokenObj instanceof String) {
            String token = (String) tokenObj;
            return findByToken(token);
        }
        return Optional.empty();
    }
    
    public Optional<PendingUserData> findByUsername(String username) {
        String usernameKey = USERNAME_INDEX_PREFIX + username;
        Object tokenObj = redisTemplate.opsForValue().get(usernameKey);
        
        if (tokenObj instanceof String) {
            String token = (String) tokenObj;
            return findByToken(token);
        }
        return Optional.empty();
    }
    
    public boolean existsByEmail(String email) {
        String emailKey = EMAIL_INDEX_PREFIX + email;
        return Boolean.TRUE.equals(redisTemplate.hasKey(emailKey));
    }
    
    public boolean existsByUsername(String username) {
        String usernameKey = USERNAME_INDEX_PREFIX + username;
        return Boolean.TRUE.equals(redisTemplate.hasKey(usernameKey));
    }
    
    public void deleteByToken(String token) {
        // Obtener datos para eliminar índices
        Optional<PendingUserData> pendingUser = findByToken(token);
        
        if (pendingUser.isPresent()) {
            PendingUserData user = pendingUser.get();
            
            // Eliminar datos principales
            String key = PENDING_USER_PREFIX + token;
            redisTemplate.delete(key);
            
            // Eliminar índices
            String emailKey = EMAIL_INDEX_PREFIX + user.getEmail();
            String usernameKey = USERNAME_INDEX_PREFIX + user.getUsername();
            String tokenKey = TOKEN_INDEX_PREFIX + token;
            
            redisTemplate.delete(emailKey);
            redisTemplate.delete(usernameKey);
            redisTemplate.delete(tokenKey);
        }
    }
    
    public void deleteByEmail(String email) {
        Optional<PendingUserData> pendingUser = findByEmail(email);
        if (pendingUser.isPresent()) {
            deleteByToken(pendingUser.get().getVerificationToken());
        }
    }
    
    public void deleteByUsername(String username) {
        Optional<PendingUserData> pendingUser = findByUsername(username);
        if (pendingUser.isPresent()) {
            deleteByToken(pendingUser.get().getVerificationToken());
        }
    }
    
    public Set<String> getAllPendingTokens() {
        String pattern = PENDING_USER_PREFIX + "*";
        return redisTemplate.keys(pattern);
    }
    
    public void extendTokenExpiration(String token, long hours) {
        String key = PENDING_USER_PREFIX + token;
        redisTemplate.expire(key, hours, TimeUnit.HOURS);
        
        // Extender también los índices
        Optional<PendingUserData> pendingUser = findByToken(token);
        if (pendingUser.isPresent()) {
            PendingUserData user = pendingUser.get();
            String emailKey = EMAIL_INDEX_PREFIX + user.getEmail();
            String usernameKey = USERNAME_INDEX_PREFIX + user.getUsername();
            String tokenKey = TOKEN_INDEX_PREFIX + token;
            
            redisTemplate.expire(emailKey, hours, TimeUnit.HOURS);
            redisTemplate.expire(usernameKey, hours, TimeUnit.HOURS);
            redisTemplate.expire(tokenKey, hours, TimeUnit.HOURS);
        }
    }
    
    public long getTokenTTL(String token) {
        String key = PENDING_USER_PREFIX + token;
        return redisTemplate.getExpire(key, TimeUnit.SECONDS);
    }
}
