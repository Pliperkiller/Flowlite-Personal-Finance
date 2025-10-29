package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.dto.UpdateUserInfoRequest;
import com.flowlite.identifyservice.application.services.CompleteInfoUserService;
import com.flowlite.identifyservice.domain.entities.UserInfo;
import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import com.flowlite.identifyservice.infrastructure.security.jwt.JwtTokenProvider;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Controlador para la gestión de información personal de usuarios
 */
@RestController
@RequestMapping("/user-info")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "User Information", description = "Endpoints para gestión de información personal de usuarios. " +
        "Requiere autenticación JWT. Permite actualizar y consultar información personal del usuario autenticado.")
public class UserInfoController {

    private final CompleteInfoUserService completeInfoUserService;
    private final JwtTokenProvider jwtTokenProvider;

    @PutMapping("/update")
    @Operation(
        summary = "Actualizar información personal del usuario autenticado",
        description = "Permite al usuario autenticado actualizar su información personal completa. " +
                     "Requiere header Authorization: Bearer TOKEN. " +
                     "Valida que el número de identificación y teléfono no estén en uso por otros usuarios. " +
                     "**Endpoint PROTEGIDO** - Requiere autenticación JWT."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Información actualizada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos de entrada inválidos o duplicados"),
        @ApiResponse(responseCode = "401", description = "Token JWT inválido o expirado"),
        @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<?> updateUserInfo(
            @Parameter(description = "Token JWT en formato Bearer", required = true)
            @RequestHeader("Authorization") String authorization,
            @Valid @RequestBody UpdateUserInfoRequest request) {
        
        try {
            // Validar y extraer token JWT
            if (authorization == null || !authorization.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token no proporcionado",
                    "message", "Debe proporcionar el token en el header Authorization: Bearer TOKEN"
                ));
            }
            
            String token = authorization.replace("Bearer ", "");
            
            // Verificar si el token está revocado
            if (jwtTokenProvider.isTokenRevoked(token)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "error", "Token revocado",
                    "message", "El token ha sido revocado y no puede ser usado"
                ));
            }
            
            // Verificar si el token es válido
            if (!jwtTokenProvider.validateToken(token)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "error", "Token inválido",
                    "message", "El token es inválido o ha expirado"
                ));
            }
            
            // Extraer userId del token
            String userIdStr = jwtTokenProvider.getUserIdFromToken(token);
            if (userIdStr == null) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token inválido",
                    "message", "No se pudo extraer el ID del usuario del token"
                ));
            }
            
            UUID userId = UUID.fromString(userIdStr);
            
            // Validar que el número de identificación no esté en uso por otro usuario
            if (completeInfoUserService.isIdentificationInUse(request.getNumeroIdentificacion())) {
                // Verificar si el número ya pertenece al usuario actual
                Optional<UserInfo> existingInfo = completeInfoUserService.getUserInfo(userId);
                if (existingInfo.isEmpty() || 
                    !request.getNumeroIdentificacion().equals(existingInfo.get().getNumeroIdentificacion())) {
                    return ResponseEntity.badRequest().body(Map.of(
                        "error", "Número de identificación en uso",
                        "message", "El número de identificación ya está registrado por otro usuario"
                    ));
                }
            }
            
            // Validar que el teléfono no esté en uso por otro usuario
            if (completeInfoUserService.isPhoneInUse(request.getTelefono())) {
                // Verificar si el teléfono ya pertenece al usuario actual
                Optional<UserInfo> existingInfo = completeInfoUserService.getUserInfo(userId);
                if (existingInfo.isEmpty() || 
                    !request.getTelefono().equals(existingInfo.get().getTelefono())) {
                    return ResponseEntity.badRequest().body(Map.of(
                        "error", "Teléfono en uso",
                        "message", "El número de teléfono ya está registrado por otro usuario"
                    ));
                }
            }
            
            // Convertir tipo de identificación
            IdentificationType tipoIdentificacion;
            try {
                tipoIdentificacion = IdentificationType.fromCode(request.getTipoIdentificacion());
            } catch (IllegalArgumentException e) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Tipo de identificación inválido",
                    "message", "El tipo de identificación proporcionado no es válido"
                ));
            }
            
            // Actualizar información del usuario
            UserInfo updatedUserInfo = completeInfoUserService.saveUserInfo(
                userId,
                request.getPrimerNombre(),
                request.getSegundoNombre(),
                request.getPrimerApellido(),
                request.getSegundoApellido(),
                request.getTelefono(),
                request.getDireccion(),
                request.getCiudad(),
                request.getDepartamento(),
                request.getPais(),
                request.getFechaNacimiento(),
                request.getNumeroIdentificacion(),
                tipoIdentificacion,
                request.getGenero(),
                request.getEstadoCivil(),
                request.getOcupacion()
            );
            
            log.info("Información personal actualizada para usuario: {}", userId);
            
            Map<String, Object> userInfoMap = new HashMap<>();
            userInfoMap.put("id", updatedUserInfo.getId());
            userInfoMap.put("userId", updatedUserInfo.getUserId());
            userInfoMap.put("nombreCompleto", updatedUserInfo.getNombreCompleto());
            userInfoMap.put("telefono", updatedUserInfo.getTelefono());
            userInfoMap.put("ciudad", updatedUserInfo.getCiudad());
            userInfoMap.put("departamento", updatedUserInfo.getDepartamento());
            userInfoMap.put("numeroIdentificacion", updatedUserInfo.getNumeroIdentificacion());
            userInfoMap.put("tipoIdentificacion", updatedUserInfo.getTipoIdentificacion() != null ? 
                updatedUserInfo.getTipoIdentificacion().getDescription() : null);
            userInfoMap.put("isComplete", updatedUserInfo.tieneInformacionCompleta());
            
            return ResponseEntity.ok(Map.of(
                "message", "Información personal actualizada exitosamente",
                "userInfo", userInfoMap
            ));
            
        } catch (IllegalArgumentException e) {
            log.warn("Error de validación al actualizar información personal: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Datos inválidos",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error al actualizar información personal del usuario", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }

    @GetMapping("/me")
    @Operation(
        summary = "Obtener información personal del usuario autenticado",
        description = "Devuelve la información personal del usuario autenticado basada en el token JWT. " +
                     "Requiere header Authorization: Bearer TOKEN. " +
                     "**Endpoint PROTEGIDO** - Requiere autenticación JWT."
    )
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Información personal obtenida exitosamente"),
        @ApiResponse(responseCode = "404", description = "Usuario no tiene información personal registrada"),
        @ApiResponse(responseCode = "401", description = "Token JWT inválido o expirado"),
        @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    @SecurityRequirement(name = "bearerAuth")
    public ResponseEntity<?> getUserInfo(
            @Parameter(description = "Token JWT en formato Bearer", required = true)
            @RequestHeader("Authorization") String authorization) {
        
        try {
            // Validar y extraer token JWT
            if (authorization == null || !authorization.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token no proporcionado",
                    "message", "Debe proporcionar el token en el header Authorization: Bearer TOKEN"
                ));
            }
            
            String token = authorization.replace("Bearer ", "");
            
            // Verificar si el token está revocado
            if (jwtTokenProvider.isTokenRevoked(token)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "error", "Token revocado",
                    "message", "El token ha sido revocado y no puede ser usado"
                ));
            }
            
            // Verificar si el token es válido
            if (!jwtTokenProvider.validateToken(token)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
                    "error", "Token inválido",
                    "message", "El token es inválido o ha expirado"
                ));
            }
            
            // Extraer userId del token
            String userIdStr = jwtTokenProvider.getUserIdFromToken(token);
            if (userIdStr == null) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token inválido",
                    "message", "No se pudo extraer el ID del usuario del token"
                ));
            }
            
            UUID userId = UUID.fromString(userIdStr);
            
            // Obtener información personal del usuario
            Optional<UserInfo> userInfo = completeInfoUserService.getUserInfo(userId);
            
            if (userInfo.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
                    "error", "Información no encontrada",
                    "message", "El usuario no tiene información personal registrada"
                ));
            }
            
            UserInfo info = userInfo.get();
            
            Map<String, Object> userInfoMap = new HashMap<>();
            userInfoMap.put("id", info.getId());
            userInfoMap.put("userId", info.getUserId());
            userInfoMap.put("primerNombre", info.getPrimerNombre());
            userInfoMap.put("segundoNombre", info.getSegundoNombre());
            userInfoMap.put("primerApellido", info.getPrimerApellido());
            userInfoMap.put("segundoApellido", info.getSegundoApellido());
            userInfoMap.put("nombreCompleto", info.getNombreCompleto());
            userInfoMap.put("telefono", info.getTelefono());
            userInfoMap.put("direccion", info.getDireccion());
            userInfoMap.put("ciudad", info.getCiudad());
            userInfoMap.put("departamento", info.getDepartamento());
            userInfoMap.put("pais", info.getPais());
            userInfoMap.put("fechaNacimiento", info.getFechaNacimiento());
            userInfoMap.put("numeroIdentificacion", info.getNumeroIdentificacion());
            userInfoMap.put("tipoIdentificacion", info.getTipoIdentificacion() != null ? 
                info.getTipoIdentificacion().getDescription() : null);
            userInfoMap.put("genero", info.getGenero());
            userInfoMap.put("estadoCivil", info.getEstadoCivil());
            userInfoMap.put("ocupacion", info.getOcupacion());
            userInfoMap.put("isComplete", info.tieneInformacionCompleta());
            userInfoMap.put("activo", info.isActivo());
            userInfoMap.put("createdAt", info.getCreatedAt());
            userInfoMap.put("updatedAt", info.getUpdatedAt());
            
            return ResponseEntity.ok(Map.of("userInfo", userInfoMap));
            
        } catch (Exception e) {
            log.error("Error al obtener información personal del usuario", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Error interno del servidor",
                "message", "Ocurrió un error inesperado al procesar la solicitud"
            ));
        }
    }
}
