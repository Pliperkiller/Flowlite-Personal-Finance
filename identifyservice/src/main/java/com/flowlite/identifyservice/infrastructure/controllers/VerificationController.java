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
    public ResponseEntity<String> verifyEmailGet(@RequestParam String token) {
        try {
            preregisterUserService.verifyAndRegister(token);
            
            // Retornar la plantilla HTML de éxito
            return ResponseEntity.ok()
                .header("Content-Type", "text/html; charset=UTF-8")
                .body(getSuccessHtmlTemplate());
            
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest()
                .header("Content-Type", "text/html; charset=UTF-8")
                .body(getErrorHtmlTemplate(e.getMessage()));
        }
    }
    
    private String getSuccessHtmlTemplate() {
        return """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>¡Cuenta activada con éxito!</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #F9FAFB; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 18px rgba(16,24,40,0.06); }
                    h1 { color: #1F2937; margin-bottom: 20px; }
                    p { color: #4B5563; font-size: 16px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>¡Cuenta activada con éxito!</h1>
                    <p>Tu cuenta ha sido activada correctamente.<br>Ya puedes iniciar sesión y disfrutar de todos los beneficios.</p>
                </div>
            </body>
            </html>
            """;
    }
    
    private String getErrorHtmlTemplate(String errorMessage) {
        return String.format("""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Error de verificación</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #F9FAFB; }
                    .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 18px rgba(16,24,40,0.06); }
                    h1 { color: #DC2626; margin-bottom: 20px; }
                    p { color: #4B5563; font-size: 16px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Error de verificación</h1>
                    <p>%s</p>
                </div>
            </body>
            </html>
            """, errorMessage);
    }
}
