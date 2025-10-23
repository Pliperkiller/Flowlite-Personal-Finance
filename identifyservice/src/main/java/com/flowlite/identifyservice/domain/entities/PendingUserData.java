package com.flowlite.identifyservice.domain.entities;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PendingUserData {
    
    private String username;
    private String email;
    private String password; // Encriptada
    private String verificationToken;
    private LocalDateTime createdAt;
    private LocalDateTime tokenExpiration;
    private Boolean isVerified;
    
    // Métodos de utilidad
    public boolean isTokenExpired() {
        return LocalDateTime.now().isAfter(tokenExpiration);
    }
    
    public boolean canBeVerified() {
        return !isVerified && !isTokenExpired();
    }
}
