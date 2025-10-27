package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

/**
 * DTO para resetear contraseña con token
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Solicitud para resetear contraseña con token")
public class ResetPasswordRequest {

    @NotBlank(message = "El token es obligatorio")
    @Schema(description = "Token de recuperación de contraseña", 
            example = "eyJhbGciOiJIUzI1NiJ9...", required = true)
    String token;

    @NotBlank(message = "La nueva contraseña es obligatoria")
    @Size(min = 8, max = 128, message = "La contraseña debe tener entre 8 y 128 caracteres")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).*$", 
             message = "La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial")
    @Schema(description = "Nueva contraseña del usuario", 
            example = "NewPassword123!", required = true)
    String newPassword;
}
