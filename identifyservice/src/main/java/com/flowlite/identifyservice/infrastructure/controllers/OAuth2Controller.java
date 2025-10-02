package com.flowlite.identifyservice.infrastructure.controllers;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/oauth2")
@Tag(name = "OAuth2", description = "Endpoints para autenticación OAuth2 con proveedores externos")
public class OAuth2Controller {

    @GetMapping("/authorization/google")
    @Operation(
        summary = "Iniciar autenticación OAuth2 con Google",
        description = """
            Inicia el flujo de autenticación OAuth2 con Google.
            Redirige al usuario a Google para autorización.
            Después de autorizar, Google redirige de vuelta con un código de autorización.
            
            **Flujo:**
            1. Usuario accede a este endpoint
            2. Se redirige a Google para autorización
            3. Google redirige de vuelta a `/login/oauth2/code/google`
            4. Se genera un JWT token y se devuelve al usuario
            """
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "302", description = "Redirección a Google para autorización"),
        @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Map<String, String>> initiateGoogleOAuth2() {
        // Este endpoint es manejado automáticamente por Spring Security
        // No necesita implementación manual
        return ResponseEntity.ok(Map.of(
            "message", "Redirigiendo a Google para autorización",
            "note", "Este endpoint es manejado automáticamente por Spring Security"
        ));
    }
}
