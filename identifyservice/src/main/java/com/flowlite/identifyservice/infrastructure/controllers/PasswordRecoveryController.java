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
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
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

    @PostMapping("/forgot-password")
    @Operation(summary = "Solicitar recuperación de contraseña",
               description = "Envía un email con enlace para recuperar la contraseña. " +
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
    public ResponseEntity<Map<String, Object>> forgotPassword(@Valid @RequestBody PasswordRecoveryRequest request) {
        try {
            log.info("Solicitud de recuperación de contraseña para email: {}", request.getEmail());
            
            Map<String, Object> result = passwordRecoveryService.requestPasswordRecovery(request.getEmail());
            
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en solicitud de recuperación: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Datos inválidos",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error al procesar solicitud de recuperación de contraseña", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }

    @PostMapping("/reset-password")
    @Operation(summary = "Resetear contraseña con token",
               description = "Resetea la contraseña usando el token de recuperación recibido por email. " +
                           "El token debe ser válido y no expirado. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Contraseña actualizada exitosamente",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "Token inválido o datos incorrectos",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        try {
            log.info("Intento de reset de contraseña con token");
            
            Map<String, Object> result = passwordRecoveryService.resetPassword(request.getToken(), request.getNewPassword());
            
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en reset de contraseña: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Datos inválidos",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error al resetear contraseña", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }

    @GetMapping("/validate-recovery-token")
    @Operation(summary = "Validar token de recuperación",
               description = "Valida si un token de recuperación es válido y no expirado. " +
                           "Útil para verificar el estado del token antes de mostrar el formulario de reset. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Token validado",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "Token inválido",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> validateRecoveryToken(@RequestParam String token) {
        try {
            log.info("Validación de token de recuperación");
            
            Map<String, Object> result = passwordRecoveryService.validateRecoveryToken(token);
            
            boolean isValid = (Boolean) result.get("valid");
            if (isValid) {
                return ResponseEntity.ok(result);
            } else {
                return ResponseEntity.badRequest().body(result);
            }
            
        } catch (Exception e) {
            log.error("Error al validar token de recuperación", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            ));
        }
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
}
