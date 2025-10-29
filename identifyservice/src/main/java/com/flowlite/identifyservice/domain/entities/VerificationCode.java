package com.flowlite.identifyservice.domain.entities;

import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entidad que representa un código de verificación de 6 dígitos
 * para recuperación de contraseñas
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(of = "id")
public class VerificationCode {
    
    UUID id;
    String code; // Código de 6 dígitos
    String email; // Email asociado al código
    String token; // Token asociado al código
    LocalDateTime createdAt;
    LocalDateTime expiresAt;
    boolean used; // Si el código ya fue usado
    int attempts; // Número de intentos de verificación
    
    /**
     * Verifica si el código ha expirado
     */
    public boolean isExpired() {
        return LocalDateTime.now().isAfter(expiresAt);
    }
    
    /**
     * Verifica si el código es válido (no usado y no expirado)
     */
    public boolean isValid() {
        return !used && !isExpired();
    }
    
    /**
     * Marca el código como usado
     */
    public void markAsUsed() {
        this.used = true;
    }
    
    /**
     * Incrementa el número de intentos
     */
    public void incrementAttempts() {
        this.attempts++;
    }
    
    /**
     * Verifica si se ha excedido el número máximo de intentos
     */
    public boolean hasExceededMaxAttempts(int maxAttempts) {
        return attempts >= maxAttempts;
    }
}
