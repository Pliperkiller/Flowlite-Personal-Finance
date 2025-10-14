package com.flowlite.identifyservice.application.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class LogoutUserService {

    private final TokenRevocationService tokenRevocationService;

    /**
     * Cierra la sesión del usuario revocando su token JWT
     * 
     * @param token El token JWT a revocar
     * @return true si el logout fue exitoso, false si el token no es válido
     */
    public boolean logout(String token) {
        return tokenRevocationService.revokeToken(token);
    }

    /**
     * Verifica si un token está revocado
     * 
     * @param token El token a verificar
     * @return true si el token está revocado, false si es válido
     */
    public boolean isTokenRevoked(String token) {
        return tokenRevocationService.isTokenRevoked(token);
    }

    /**
     * Valida un token (verifica que no esté revocado y sea válido)
     * 
     * @param token El token a validar
     * @return true si el token es válido y no está revocado
     */
    public boolean validateToken(String token) {
        return tokenRevocationService.validateToken(token);
    }
}
