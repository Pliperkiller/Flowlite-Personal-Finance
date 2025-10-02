package com.flowlite.identifyservice.infrastructure.controllers;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@Tag(name = "Protected Endpoints", description = "Endpoints que requieren autenticación JWT")
@SecurityRequirement(name = "Bearer Authentication")
public class ProtectedController {

    @GetMapping("/profile")
    @Operation(
        summary = "Obtener perfil del usuario autenticado",
        description = "Devuelve la información del perfil del usuario autenticado usando el JWT token."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Perfil obtenido exitosamente",
                content = @Content(mediaType = "application/json",
                        examples = @ExampleObject(value = """
                            {
                                "username": "johndoe",
                                "email": "john@example.com",
                                "role": "USER",
                                "active": true
                            }
                            """))),
        @ApiResponse(responseCode = "401", description = "Token JWT inválido o expirado",
                content = @Content(mediaType = "application/json",
                        examples = @ExampleObject(value = "{\"error\": \"Unauthorized\"}"))),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    })
    public ResponseEntity<Map<String, Object>> getProfile() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        if (authentication != null && authentication.isAuthenticated()) {
            return ResponseEntity.ok(Map.of(
                "message", "Perfil del usuario autenticado",
                "username", authentication.getName(),
                "authorities", authentication.getAuthorities(),
                "authenticated", true
            ));
        }
        
        return ResponseEntity.ok(Map.of(
            "message", "Usuario no autenticado",
            "authenticated", false
        ));
    }

    @GetMapping("/protected")
    @Operation(
        summary = "Endpoint protegido de ejemplo",
        description = "Endpoint de ejemplo que requiere autenticación JWT para acceder."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Acceso exitoso al endpoint protegido",
                content = @Content(mediaType = "application/json",
                        examples = @ExampleObject(value = """
                            {
                                "message": "Acceso exitoso al endpoint protegido",
                                "timestamp": "2025-09-28T22:30:00Z",
                                "user": "johndoe"
                            }
                            """))),
        @ApiResponse(responseCode = "401", description = "Token JWT inválido o expirado"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado")
    })
    public ResponseEntity<Map<String, Object>> protectedEndpoint() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        return ResponseEntity.ok(Map.of(
            "message", "Acceso exitoso al endpoint protegido",
            "timestamp", java.time.Instant.now().toString(),
            "user", authentication != null ? authentication.getName() : "anonymous",
            "authenticated", authentication != null && authentication.isAuthenticated()
        ));
    }

    @GetMapping("/admin")
    @Operation(
        summary = "Endpoint de administrador",
        description = "Endpoint que requiere rol de administrador para acceder."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Acceso exitoso como administrador"),
        @ApiResponse(responseCode = "401", description = "Token JWT inválido o expirado"),
        @ApiResponse(responseCode = "403", description = "Acceso denegado - se requiere rol de administrador")
    })
    public ResponseEntity<Map<String, Object>> adminEndpoint() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        return ResponseEntity.ok(Map.of(
            "message", "Acceso exitoso como administrador",
            "timestamp", java.time.Instant.now().toString(),
            "user", authentication != null ? authentication.getName() : "anonymous",
            "role", "ADMIN"
        ));
    }
}
