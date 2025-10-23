package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.services.PreregisterUserService;
import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.infrastructure.dtos.PreregisterResponse;
import com.flowlite.identifyservice.infrastructure.dtos.VerificationRequest;
import com.flowlite.identifyservice.infrastructure.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.Map;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Tag(name = "Email Verification", description = "Endpoints para verificación de email y preregistro. " +
        "Incluye preregistro con verificación de email y activación de cuentas. " +
        "Flujo: Preregistro → Email de verificación → Verificación → Registro final. " +
        "Requiere verificación de email antes de completar el registro.")
public class VerificationController {

    private final PreregisterUserService preregisterUserService;
    private final JwtTokenProvider tokenProvider;

    @PostMapping("/preregister")
    @Operation(summary = "Preregistro de usuario con verificación de email", 
               description = "Inicia el proceso de registro enviando un email de verificación. " +
                           "El usuario debe verificar su email antes de completar el registro. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Preregistro exitoso - Email de verificación enviado",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = """
                                {
                                    "message": "Preregistro exitoso",
                                    "status": "success",
                                    "email": "usuario@example.com",
                                    "note": "Revisa tu email para verificar tu cuenta. El enlace será válido por 24 horas."
                                }
                                """))),
            @ApiResponse(responseCode = "400", description = "Error de validación o datos duplicados",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = """
                                {
                                    "error": "Error de validación",
                                    "message": "Los campos requeridos no pueden estar vacíos o tienen formato inválido",
                                    "details": {
                                        "email": "El email ya está registrado"
                                    },
                                    "status": "BAD_REQUEST"
                                }
                                """))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Object> preregister(@Valid @RequestBody com.flowlite.identifyservice.infrastructure.dtos.PreregisterRequest request) {
        try {
            preregisterUserService.preregister(request);
            
            PreregisterResponse response = PreregisterResponse.builder()
                .message("Preregistro exitoso")
                .status("success")
                .email(request.getEmail())
                .note("Revisa tu email para verificar tu cuenta. El enlace será válido por 24 horas.")
                .build();
            
            return ResponseEntity.ok(response);
            
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Error en el preregistro",
                "message", e.getMessage(),
                "status", "BAD_REQUEST"
            ));
        }
    }

    @PostMapping("/verify")
    @Operation(summary = "Verificar email y completar registro", 
               description = "Verifica el token de email y completa el registro del usuario. " +
                           "Después de la verificación, el usuario puede iniciar sesión. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Verificación exitosa - Usuario registrado",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = """
                                {
                                    "message": "Email verificado exitosamente",
                                    "status": "success",
                                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                    "user": {
                                        "username": "johndoe",
                                        "email": "john@example.com"
                                    }
                                }
                                """))),
            @ApiResponse(responseCode = "400", description = "Token inválido o expirado",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = """
                                {
                                    "error": "Token de verificación inválido",
                                    "message": "El token no es válido o ha expirado",
                                    "status": "BAD_REQUEST"
                                }
                                """))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Map<String, Object>> verifyEmail(@Valid @RequestBody VerificationRequest request) {
        try {
            User user = preregisterUserService.verifyAndRegister(request.getToken());
            String jwt = tokenProvider.generateToken(user);
            
            return ResponseEntity.ok(Map.of(
                "message", "Email verificado exitosamente",
                "status", "success",
                "access_token", jwt,
                "user", Map.of(
                    "username", user.getUsername(),
                    "email", user.getEmail()
                )
            ));
            
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Token de verificación inválido",
                "message", e.getMessage(),
                "status", "BAD_REQUEST"
            ));
        }
    }

    @GetMapping("/verify")
    @Operation(summary = "Verificar email desde enlace (GET)", 
               description = "Verifica el email usando el token como parámetro de URL. " +
                           "Útil para enlaces en emails. Redirige a una página de éxito. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Verificación exitosa",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = """
                                {
                                    "message": "Email verificado exitosamente",
                                    "status": "success",
                                    "redirect": "http://localhost:3000/verification-success"
                                }
                                """))),
            @ApiResponse(responseCode = "400", description = "Token inválido o expirado")
    })
    public ResponseEntity<Map<String, String>> verifyEmailGet(@RequestParam String token) {
        try {
            preregisterUserService.verifyAndRegister(token);
            
            return ResponseEntity.ok(Map.of(
                "message", "Email verificado exitosamente",
                "status", "success",
                "redirect", "http://localhost:3000/verification-success"
            ));
            
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Token de verificación inválido",
                "message", e.getMessage(),
                "status", "BAD_REQUEST"
            ));
        }
    }
}
