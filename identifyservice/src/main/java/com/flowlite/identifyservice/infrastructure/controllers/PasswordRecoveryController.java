package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.dto.PasswordRecoveryRequest;
import com.flowlite.identifyservice.application.dto.ResetPasswordRequest;
import com.flowlite.identifyservice.application.services.PasswordRecoveryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

/**
 * Controlador para gestión de recuperación de contraseñas
 */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Password Recovery", description = "Endpoints para recuperación de contraseñas y información de usuario")
public class PasswordRecoveryController {

    private final PasswordRecoveryService passwordRecoveryService;
    
    @Value("${app.password-recovery.traditional-flow-enabled:false}")
    private boolean traditionalFlowEnabled;

    @PostMapping("/forgot-password")
    @Operation(summary = "Solicitar recuperación de contraseña (DESHABILITADO)",
               description = "Este endpoint está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "400", description = "Endpoint deshabilitado",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
    })
    public ResponseEntity<Map<String, Object>> forgotPassword(@Valid @RequestBody PasswordRecoveryRequest request) {
        log.warn("Intento de usar endpoint deshabilitado /auth/forgot-password para email: {}", request.getEmail());
        
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Endpoint deshabilitado",
            "message", "El flujo tradicional de recuperación de contraseña está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación.",
            "alternative_endpoint", "/auth/forgot-password-code",
            "status", "DISABLED"
        ));
    }

    @PostMapping("/reset-password")
    @Operation(summary = "Resetear contraseña con token (DESHABILITADO)",
               description = "Este endpoint está deshabilitado. Use /auth/reset-password-code para reset con códigos de verificación. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "400", description = "Endpoint deshabilitado",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
    })
    public ResponseEntity<Map<String, Object>> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        log.warn("Intento de usar endpoint deshabilitado /auth/reset-password");
        
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Endpoint deshabilitado",
            "message", "El flujo tradicional de reset de contraseña está deshabilitado. Use /auth/reset-password-code para reset con códigos de verificación.",
            "alternative_endpoint", "/auth/reset-password-code",
            "status", "DISABLED"
        ));
    }

    /**
     * Endpoint GET para mostrar el formulario de reseteo de contraseña.
     * Valida el token y muestra un formulario HTML si es válido.
     *
     * @param token El token de recuperación.
     * @return HTML con formulario de reseteo o página de error.
     */
    @GetMapping("/reset-password")
    @Operation(summary = "Mostrar formulario de reseteo de contraseña (DESHABILITADO)",
               description = "Este endpoint está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación. " +
                             "**Endpoint PÚBLICO** - No requiere autenticación.")
    public ResponseEntity<String> showResetPasswordForm(@RequestParam String token) {
        log.warn("Intento de usar endpoint deshabilitado GET /auth/reset-password");
        
        String errorPage = createErrorPage(
            "Endpoint Deshabilitado", 
            "El flujo tradicional de recuperación de contraseña está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación."
        );
        return ResponseEntity.ok().contentType(org.springframework.http.MediaType.TEXT_HTML).body(errorPage);
    }

    /**
     * Endpoint para resetear contraseña desde formulario HTML (application/x-www-form-urlencoded)
     */
    @PostMapping(value = "/reset-password", consumes = "application/x-www-form-urlencoded")
    @Operation(summary = "Resetear contraseña desde formulario web (DESHABILITADO)",
               description = "Este endpoint está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación. " +
                             "**Endpoint PÚBLICO** - No requiere autenticación.")
    public ResponseEntity<String> resetPasswordFromForm(@RequestParam String token, @RequestParam String newPassword) {
        log.warn("Intento de usar endpoint deshabilitado POST /auth/reset-password (formulario)");
        
        String errorPage = createErrorPage(
            "Endpoint Deshabilitado", 
            "El flujo tradicional de recuperación de contraseña está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación."
        );
        return ResponseEntity.ok().contentType(org.springframework.http.MediaType.TEXT_HTML).body(errorPage);
    }

    @GetMapping("/validate-recovery-token")
    @Operation(summary = "Validar token de recuperación (DESHABILITADO)",
               description = "Este endpoint está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "400", description = "Endpoint deshabilitado",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
    })
    public ResponseEntity<Map<String, Object>> validateRecoveryToken(@RequestParam String token) {
        log.warn("Intento de usar endpoint deshabilitado /auth/validate-recovery-token");
        
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Endpoint deshabilitado",
            "message", "El flujo tradicional de validación de token está deshabilitado. Use /auth/forgot-password-code para recuperación con códigos de verificación.",
            "alternative_endpoint", "/auth/forgot-password-code",
            "status", "DISABLED"
        ));
    }

    @PostMapping("/forgot-username")
    @Operation(summary = "Recuperar información de usuario",
               description = "Envía un email con la información del usuario (username) asociado al email. " +
                           "Por seguridad, siempre devuelve éxito independientemente de si el email existe. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Solicitud procesada exitosamente",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "Email inválido",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> forgotUsername(@Valid @RequestBody PasswordRecoveryRequest request) {
        try {
            log.info("Solicitud de información de usuario para email: {}", request.getEmail());
            
            Map<String, Object> result = passwordRecoveryService.getUserInfoByEmail(request.getEmail());
            
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en solicitud de información de usuario: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Datos inválidos",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error al procesar solicitud de información de usuario", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }

    /**
     * Crea el formulario HTML para reseteo de contraseña usando template
     */
    private String createResetPasswordForm(String token) {
        try {
            String template = Files.readString(Paths.get("src/main/resources/templates/email/reset-password-form.html"));
            return template.replace("{token}", token);
        } catch (IOException e) {
            log.error("Error al leer template de formulario de reseteo: {}", e.getMessage());
            return createBasicResetForm(token);
        }
    }

    /**
     * Formulario básico de reseteo como fallback
     */
    private String createBasicResetForm(String token) {
        return "<!DOCTYPE html>" +
                "<html><head><title>Recuperar Contraseña</title></head>" +
                "<body><h1>Recuperar Contraseña</h1>" +
                "<form method=\"POST\" action=\"/auth/reset-password\">" +
                "<input type=\"hidden\" name=\"token\" value=\"" + token + "\">" +
                "<label>Nueva Contraseña: <input type=\"password\" name=\"newPassword\" required></label><br><br>" +
                "<button type=\"submit\">Cambiar Contraseña</button>" +
                "</form></body></html>";
    }

    /**
     * Crea una página de error HTML usando template
     */
    private String createErrorPage(String title, String message) {
        try {
            String template = Files.readString(Paths.get("src/main/resources/templates/email/reset-password-error.html"));
            return template.replace("{title}", title).replace("{message}", message);
        } catch (IOException e) {
            log.error("Error al leer template de página de error: {}", e.getMessage());
            return createBasicErrorPage(title, message);
        }
    }

    /**
     * Página de error básica como fallback
     */
    private String createBasicErrorPage(String title, String message) {
        return "<!DOCTYPE html>" +
                "<html><head><title>Error</title></head>" +
                "<body><h1>" + title + "</h1>" +
                "<p>" + message + "</p>" +
                "<a href=\"/\">Volver al inicio</a>" +
                "</body></html>";
    }

    /**
     * Crea una página de éxito HTML usando template
     */
    private String createSuccessPage() {
        try {
            String template = Files.readString(Paths.get("src/main/resources/templates/email/reset-password-success.html"));
            return template;
        } catch (IOException e) {
            log.error("Error al leer template de página de éxito: {}", e.getMessage());
            return createBasicSuccessPage();
        }
    }

    /**
     * Página de éxito básica como fallback
     */
    private String createBasicSuccessPage() {
        return "<!DOCTYPE html>" +
                "<html><head><title>Contraseña Cambiada</title></head>" +
                "<body><h1>¡Contraseña cambiada exitosamente!</h1>" +
                "<p>Tu contraseña ha sido actualizada correctamente.</p>" +
                "<a href=\"/\">Volver al inicio</a>" +
                "</body></html>";
    }
}
