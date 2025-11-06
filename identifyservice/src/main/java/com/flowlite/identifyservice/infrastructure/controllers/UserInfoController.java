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
 * Controller for managing user's personal information
 */
@RestController
@RequestMapping("/user-info")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "User Information", description = "Endpoints for managing user's personal information. " +
        "Requires JWT authentication. Allows updating and querying authenticated user's personal information.")
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
            
            // Validate that identification number is not already in use by another user
            if (completeInfoUserService.isIdentificationInUse(request.getIdentificationNumber())) {
                // Check if the number already belongs to the current user
                Optional<UserInfo> existingInfo = completeInfoUserService.getUserInfo(userId);
                if (existingInfo.isEmpty() ||
                    !request.getIdentificationNumber().equals(existingInfo.get().getIdentificationNumber())) {
                    return ResponseEntity.badRequest().body(Map.of(
                        "error", "Identification number in use",
                        "message", "The identification number is already registered by another user"
                    ));
                }
            }

            // Validate that phone is not already in use by another user
            if (completeInfoUserService.isPhoneInUse(request.getPhone())) {
                // Check if the phone already belongs to the current user
                Optional<UserInfo> existingInfo = completeInfoUserService.getUserInfo(userId);
                if (existingInfo.isEmpty() ||
                    !request.getPhone().equals(existingInfo.get().getPhone())) {
                    return ResponseEntity.badRequest().body(Map.of(
                        "error", "Phone number in use",
                        "message", "The phone number is already registered by another user"
                    ));
                }
            }

            // Convert identification type
            IdentificationType identificationType;
            try {
                identificationType = IdentificationType.fromCode(request.getIdentificationType());
            } catch (IllegalArgumentException e) {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Invalid identification type",
                    "message", "The provided identification type is not valid"
                ));
            }

            // Update user information
            UserInfo updatedUserInfo = completeInfoUserService.saveUserInfo(
                userId,
                request.getFirstName(),
                request.getMiddleName(),
                request.getLastName(),
                request.getSecondLastName(),
                request.getPhone(),
                request.getAddress(),
                request.getCity(),
                request.getState(),
                request.getCountry(),
                request.getBirthDate(),
                request.getIdentificationNumber(),
                identificationType,
                request.getGender(),
                request.getMaritalStatus(),
                request.getOccupation()
            );

            log.info("Personal information updated for user: {}", userId);

            Map<String, Object> userInfoMap = new HashMap<>();
            userInfoMap.put("id", updatedUserInfo.getId());
            userInfoMap.put("userId", updatedUserInfo.getUserId());
            userInfoMap.put("fullName", updatedUserInfo.getFullName());
            userInfoMap.put("phone", updatedUserInfo.getPhone());
            userInfoMap.put("city", updatedUserInfo.getCity());
            userInfoMap.put("state", updatedUserInfo.getState());
            userInfoMap.put("identificationNumber", updatedUserInfo.getIdentificationNumber());
            userInfoMap.put("identificationType", updatedUserInfo.getIdentificationType() != null ?
                updatedUserInfo.getIdentificationType().getDescription() : null);
            userInfoMap.put("isComplete", updatedUserInfo.hasCompleteInformation());
            
            return ResponseEntity.ok(Map.of(
                "message", "Personal information updated successfully",
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
            userInfoMap.put("firstName", info.getFirstName());
            userInfoMap.put("middleName", info.getMiddleName());
            userInfoMap.put("lastName", info.getLastName());
            userInfoMap.put("secondLastName", info.getSecondLastName());
            userInfoMap.put("fullName", info.getFullName());
            userInfoMap.put("phone", info.getPhone());
            userInfoMap.put("address", info.getAddress());
            userInfoMap.put("city", info.getCity());
            userInfoMap.put("state", info.getState());
            userInfoMap.put("country", info.getCountry());
            userInfoMap.put("birthDate", info.getBirthDate());
            userInfoMap.put("identificationNumber", info.getIdentificationNumber());
            userInfoMap.put("identificationType", info.getIdentificationType() != null ?
                info.getIdentificationType().getDescription() : null);
            userInfoMap.put("gender", info.getGender());
            userInfoMap.put("maritalStatus", info.getMaritalStatus());
            userInfoMap.put("occupation", info.getOccupation());
            userInfoMap.put("isComplete", info.hasCompleteInformation());
            userInfoMap.put("active", info.isActive());
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
