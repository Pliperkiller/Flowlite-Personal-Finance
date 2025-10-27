package com.flowlite.identifyservice.infrastructure.dtos;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

@Data
public class VerificationRequest {
    @NotBlank(message = "El token de verificación es obligatorio")
    private String token;
}

