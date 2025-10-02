package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.ports.TokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Tag(name = "Token Management", description = "Endpoints para validación y gestión de tokens JWT")
public class TokenController {

    private final TokenProvider tokenProvider;

    @PostMapping("/validate")
    @Operation(
        summary = "Validar token JWT",
        description = "Valida si un token JWT es válido y no ha expirado."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Token válido",
                content = @Content(mediaType = "application/json",
                        examples = @ExampleObject(value = """
                            {
                                "valid": true,
                                "message": "Token válido",
                                "username": "johndoe",
                                "expiresAt": "2025-09-29T22:30:00Z"
                            }
                            """))),
        @ApiResponse(responseCode = "400", description = "Token inválido o expirado",
                content = @Content(mediaType = "application/json",
                        examples = @ExampleObject(value = """
                            {
                                "valid": false,
                                "message": "Token inválido o expirado",
                                "error": "JWT expired"
                            }
                            """))),
        @ApiResponse(responseCode = "401", description = "Token no proporcionado")
    })
    public ResponseEntity<Map<String, Object>> validateToken(@RequestBody TokenValidationRequest request) {
        try {
            if (request.getToken() == null || request.getToken().trim().isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of(
                    "valid", false,
                    "message", "Token no proporcionado",
                    "error", "Token is required"
                ));
            }

            boolean isValid = tokenProvider.validateToken(request.getToken());
            
            if (isValid) {
                String username = tokenProvider.getUserNameFromToken(request.getToken());
                return ResponseEntity.ok(Map.of(
                    "valid", true,
                    "message", "Token válido",
                    "username", username
                ));
            } else {
                return ResponseEntity.badRequest().body(Map.of(
                    "valid", false,
                    "message", "Token inválido o expirado",
                    "error", "Invalid or expired token"
                ));
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "valid", false,
                "message", "Error al validar token",
                "error", e.getMessage()
            ));
        }
    }

    @GetMapping("/token-info")
    @Operation(
        summary = "Obtener información del token JWT",
        description = "Extrae información del token JWT sin validarlo completamente."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Información del token obtenida"),
        @ApiResponse(responseCode = "400", description = "Error al procesar el token")
    })
    public ResponseEntity<Map<String, Object>> getTokenInfo(@RequestParam String token) {
        try {
            if (token == null || token.trim().isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token no proporcionado"
                ));
            }

            String username = tokenProvider.getUserNameFromToken(token);
            boolean isValid = tokenProvider.validateToken(token);
            
            return ResponseEntity.ok(Map.of(
                "username", username,
                "valid", isValid,
                "message", isValid ? "Token válido" : "Token inválido o expirado"
            ));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Error al procesar token: " + e.getMessage()
            ));
        }
    }

    // Clase interna para el request
    @Schema(description = "Request para validación de token")
    public static class TokenValidationRequest {
        @Schema(description = "Token JWT a validar", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        private String token;

        public String getToken() {
            return token;
        }

        public void setToken(String token) {
            this.token = token;
        }
    }
}
