package com.flowlite.identifyservice.application.ports;

import com.flowlite.identifyservice.domain.entities.User;

public interface TokenProvider {
    String generateToken(User user);
    boolean validateToken(String token);
    String getUserIdFromToken(String token); // <-- nuevo
    String getUserNameFromToken(String token);  // 👈 nuevo

}
