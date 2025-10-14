package com.flowlite.identifyservice.application.ports;

import com.flowlite.identifyservice.domain.entities.User;

public interface TokenProvider {
    String generateToken(User user);
    boolean validateToken(String token);
    String getUserIdFromToken(String token);
    String getUserNameFromToken(String token);
    void revokeToken(String token);
    boolean isTokenRevoked(String token);
}
