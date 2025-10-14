package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.application.ports.TokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * Servicio centralizado para revocación de tokens.
 * Independiente de la plataforma (web/mobile).
 */
@Service
@RequiredArgsConstructor
public class TokenRevocationService {

    private final TokenProvider tokenProvider;

    /**
     * Revoca un token independientemente de la plataforma
     * 
     * @param token El token JWT a revocar
     * @return true si el token fue revocado exitosamente, false si no es válido
     */
    public boolean revokeToken(String token) {
        try {
            // Validar que el token sea válido antes de revocarlo
            if (!tokenProvider.validateToken(token)) {
                return false;
            }
            
            // Revocar el token
            tokenProvider.revokeToken(token);
            return true;
            
        } catch (Exception e) {
            System.err.println("Error al revocar token: " + e.getMessage());
            return false;
        }
    }

    /**
     * Verifica si un token está revocado
     * 
     * @param token El token a verificar
     * @return true si el token está revocado, false si es válido
     */
    public boolean isTokenRevoked(String token) {
        return tokenProvider.isTokenRevoked(token);
    }

    /**
     * Valida un token (verifica que no esté revocado y sea válido)
     * 
     * @param token El token a validar
     * @return true si el token es válido y no está revocado
     */
    public boolean validateToken(String token) {
        return tokenProvider.validateToken(token);
    }
}
