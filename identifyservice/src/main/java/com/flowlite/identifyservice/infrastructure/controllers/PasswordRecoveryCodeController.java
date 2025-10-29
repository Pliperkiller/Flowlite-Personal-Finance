package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.infrastructure.dtos.PasswordRecoveryCodeRequest;
import com.flowlite.identifyservice.infrastructure.dtos.VerifyCodeRequest;
import com.flowlite.identifyservice.infrastructure.dtos.ResetPasswordRequest;
import com.flowlite.identifyservice.application.services.PasswordRecoveryCodeService;
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
 * Controlador para gestión de recuperación de contraseñas con códigos de verificación
 */
@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Password Recovery Code", description = "Endpoints para recuperación de contraseñas con códigos de verificación")
public class PasswordRecoveryCodeController {

    private final PasswordRecoveryCodeService passwordRecoveryCodeService;

    @PostMapping("/forgot-password-code")
    @Operation(summary = "Solicitar código de verificación para recuperación de contraseña",
               description = "Envía un email con código de verificación de 6 dígitos para recuperar la contraseña. " +
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
    public ResponseEntity<Map<String, Object>> requestPasswordRecoveryCode(@Valid @RequestBody PasswordRecoveryCodeRequest request) {
        try {
            log.info("Solicitud de código de verificación para recuperación de contraseña: {}", request.getEmail());
            
            Map<String, Object> result = passwordRecoveryCodeService.requestPasswordRecoveryCode(request.getEmail());
            
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación en solicitud de código de verificación: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Datos inválidos",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error al procesar solicitud de código de verificación", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }


    @PostMapping("/verify-code")
    @Operation(summary = "Verificar código de 6 dígitos",
               description = "Verifica el código de 6 dígitos junto con el email asociado y devuelve el token de restablecimiento de contraseña si es válido. " +
                           "Requiere tanto el código como el email para mayor seguridad. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Código verificado exitosamente",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "Código inválido o expirado",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> verifyCode(@Valid @RequestBody VerifyCodeRequest request) {
        try {
            log.info("Verificación de código: {} para email: {}", request.getCode(), request.getEmail());
            
            Map<String, Object> result = passwordRecoveryCodeService.verifyCodeAndGetResetToken(
                request.getCode(),
                request.getEmail()
            );
            
            if (Boolean.TRUE.equals(result.get("valid"))) {
                return ResponseEntity.ok(result);
            } else {
                return ResponseEntity.badRequest().body(result);
            }
            
        } catch (Exception e) {
            log.error("Error al verificar código", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "valid", false,
                "message", "Error interno del servidor"
            ));
        }
    }

    @PostMapping("/reset-password-code")
    @Operation(summary = "Restablecer contraseña con token",
               description = "Restablece la contraseña del usuario usando el token obtenido tras verificar el código. " +
                           "**Endpoint PÚBLICO** - No requiere autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Contraseña restablecida exitosamente",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "Token inválido o contraseña inválida",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor",
                         content = @Content(mediaType = "application/json",
                                            schema = @Schema(implementation = Map.class)))
    })
    public ResponseEntity<Map<String, Object>> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        try {
            log.info("Intento de reset de contraseña con token de restablecimiento");
            
            Map<String, Object> result = passwordRecoveryCodeService.resetPassword(
                request.getToken(), 
                request.getNewPassword()
            );
            
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
}
