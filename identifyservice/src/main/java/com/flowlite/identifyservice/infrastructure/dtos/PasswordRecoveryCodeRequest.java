package com.flowlite.identifyservice.infrastructure.dtos;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO para solicitar código de verificación de recuperación de contraseña
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PasswordRecoveryCodeRequest {
    
    @NotBlank(message = "El email es obligatorio")
    @Email(message = "El formato del email no es válido")
    private String email;
}
