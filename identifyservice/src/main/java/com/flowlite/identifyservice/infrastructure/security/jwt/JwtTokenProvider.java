package com.flowlite.identifyservice.infrastructure.security.jwt;

import com.flowlite.identifyservice.application.ports.TokenProvider;
import com.flowlite.identifyservice.domain.entities.User;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.security.Key;
import java.util.Date;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Set;

@Component
@RequiredArgsConstructor
public class JwtTokenProvider implements TokenProvider {

    private final JwtProperties jwtProperties;
    private final RedisTemplate<String, String> redisTemplate;
    
    // Fallback en memoria si Redis no está disponible
    private final Set<String> revokedTokens = ConcurrentHashMap.newKeySet();

    private Key getKey() {
        return Keys.hmacShaKeyFor(jwtProperties.getSecret().getBytes());
    }

    @Override
    public String generateToken(User user) {
        return Jwts.builder()
                .setSubject(user.getUsername().getValue()) // 👈 username como subject
                .claim("userId", user.getId().toString())   // 👈 opcional: ID en claims
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + jwtProperties.getExpiration()))
                .signWith(getKey(), SignatureAlgorithm.HS256)
                .compact();
    }
    
    /**
     * Genera un token JWT específico para verificación de email.
     * 
     * @param username Nombre de usuario
     * @param email Email del usuario
     * @return Token JWT firmado para verificación
     */
    public String generateVerificationToken(String username, String email) {
        return Jwts.builder()
                .setSubject(username)
                .claim("email", email)
                .claim("type", "verification")
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + jwtProperties.getExpiration()))
                .signWith(getKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    @Override
    public boolean validateToken(String token) {
        try {
            // Verificar si el token está revocado (Redis o memoria)
            if (isTokenRevoked(token)) {
                return false;
            }
            
            Jwts.parserBuilder().setSigningKey(getKey()).build().parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public String getUserNameFromToken(String token) {
        return getClaims(token).getSubject();
    }

    @Override
    public String getUserIdFromToken(String token) {
        return getClaims(token).get("userId", String.class);
    }
    
    /**
     * Extrae el email del token (para tokens de verificación).
     * 
     * @param token Token JWT
     * @return Email extraído del token
     */
    public String getEmailFromToken(String token) {
        return getClaims(token).get("email", String.class);
    }
    
    /**
     * Verifica si el token es de tipo verificación.
     * 
     * @param token Token JWT
     * @return true si es token de verificación
     */
    public boolean isVerificationToken(String token) {
        try {
            String type = getClaims(token).get("type", String.class);
            return "verification".equals(type);
        } catch (Exception e) {
            return false;
        }
    }

    private Claims getClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    @Override
    public void revokeToken(String token) {
        try {
            // Intentar usar Redis primero
            redisTemplate.opsForSet().add("revoked_tokens", token);
            System.out.println("Token revocado en Redis: " + token.substring(0, Math.min(20, token.length())) + "...");
        } catch (Exception e) {
            // Fallback a memoria si Redis no está disponible
            revokedTokens.add(token);
            System.out.println("Token revocado en memoria (Redis no disponible): " + token.substring(0, Math.min(20, token.length())) + "...");
        }
    }

    @Override
    public boolean isTokenRevoked(String token) {
        try {
            // Intentar verificar en Redis primero
            return Boolean.TRUE.equals(redisTemplate.opsForSet().isMember("revoked_tokens", token));
        } catch (Exception e) {
            // Fallback a memoria si Redis no está disponible
            return revokedTokens.contains(token);
        }
    }
}
