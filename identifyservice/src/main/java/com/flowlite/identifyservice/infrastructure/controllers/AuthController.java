package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.services.LoginUserService;
import com.flowlite.identifyservice.application.services.RegisterUserService;
import com.flowlite.identifyservice.infrastructure.dtos.LoginRequest;
import com.flowlite.identifyservice.infrastructure.dtos.RegisterRequest;
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

import java.util.Map;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Tag(name = "Authentication", description = "Endpoints para autenticación, gestión de tokens y información del usuario autenticado. " +
        "Incluye registro, login, logout, validación de tokens y obtención de información del usuario actual. " +
        "Optimizado para microservicios que necesitan identificar al usuario autenticado.")
public class AuthController {

    private final RegisterUserService registerUserService;
    private final LoginUserService loginUserService;
    private final JwtTokenProvider tokenProvider;

    @PostMapping("/register")
    @Operation(summary = "Registrar nuevo usuario", description = "Crea una nueva cuenta de usuario con email, username y contraseña. Devuelve un JWT token para autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario registrado exitosamente",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = "{\"access_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"}"))),
            @ApiResponse(responseCode = "400", description = "Error en la petición",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = "{\"error\": \"El email ya está registrado\"}"))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Map<String, String>> register(@RequestBody RegisterRequest request) {
        User user = registerUserService.register(
                request.getUsername(),
                request.getEmail(),
                request.getPassword()
        );

        String jwt = tokenProvider.generateToken(user);
        return ResponseEntity.ok(Map.of("access_token", jwt));
    }

    @PostMapping("/login")
    @Operation(summary = "Iniciar sesión", description = "Autentica un usuario existente con username/email y contraseña. Devuelve un JWT token para autenticación.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Login exitoso",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = "{\"access_token\": \"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"}"))),
            @ApiResponse(responseCode = "401", description = "Credenciales inválidas",
                    content = @Content(mediaType = "application/json",
                            examples = @ExampleObject(value = "{\"error\": \"Credenciales inválidas\"}"))),
            @ApiResponse(responseCode = "400", description = "Error en la petición"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Map<String, String>> login(@RequestBody LoginRequest request) {
        String jwt = loginUserService.login(request.getUsername(), request.getPassword());
        return ResponseEntity.ok(Map.of("access_token", jwt));
    }

    @GetMapping("/success")
    @Operation(summary = "Página de éxito de autenticación OAuth2", 
               description = "Endpoint de fallback para navegadores. Las aplicaciones móviles reciben el token " +
                           "a través del URL scheme personalizado: flowliteapp://auth/success?token=JWT_TOKEN")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Página de éxito mostrada correctamente"),
            @ApiResponse(responseCode = "400", description = "Token no proporcionado")
    })
    public ResponseEntity<Map<String, String>> oauth2Success(@RequestParam String token) {
        return ResponseEntity.ok(Map.of(
            "message", "Autenticación OAuth2 exitosa",
            "access_token", token,
            "mobile_redirect", "flowliteapp://auth/success?token=" + token,
            "note", "Las aplicaciones móviles reciben este token a través del URL scheme personalizado"
        ));
    }

    @GetMapping("/error")
    @Operation(summary = "Página de error de autenticación OAuth2", 
               description = "Endpoint de fallback para navegadores. Las aplicaciones móviles reciben el error " +
                           "a través del URL scheme personalizado: flowliteapp://auth/error?message=ERROR_MESSAGE")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "400", description = "Error en la autenticación OAuth2")
    })
    public ResponseEntity<Map<String, String>> oauth2Error(@RequestParam(required = false) String message) {
        String errorMessage = message != null ? message : "Error desconocido";
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Error en la autenticación OAuth2",
            "message", errorMessage,
            "mobile_redirect", "flowliteapp://auth/error?message=" + java.net.URLEncoder.encode(errorMessage, java.nio.charset.StandardCharsets.UTF_8),
            "note", "Las aplicaciones móviles reciben este error a través del URL scheme personalizado"
        ));
    }

    @PostMapping("/logout")
    @Operation(summary = "Cerrar sesión y revocar token", 
               description = "Invalida el token JWT del usuario, cerrando su sesión de forma segura. " +
                           "El token se agrega a Redis (blacklist) para evitar su reutilización. " +
                           "Funciona para cualquier plataforma (web/mobile). " +
                           "Acepta token en header Authorization (web) o como parámetro (mobile).")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Sesión cerrada exitosamente",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"message\":\"Sesión cerrada exitosamente\",\"status\":\"success\",\"note\":\"El token ha sido revocado y ya no es válido\"}"
                    ))),
            @ApiResponse(responseCode = "401", description = "Token inválido o expirado",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"error\":\"No se pudo cerrar la sesión\",\"message\":\"El token no es válido o ya fue revocado\"}"
                    ))),
            @ApiResponse(responseCode = "400", description = "Token no proporcionado",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"error\":\"Token no proporcionado\",\"message\":\"Debe proporcionar el token en el header Authorization o como parámetro 'token'\"}"
                    )))
    })
    public ResponseEntity<Map<String, String>> logout(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @RequestParam(value = "token", required = false) String tokenParam) {
        try {
            String token = null;
            
            // Determinar de dónde obtener el token
            if (authorization != null && authorization.startsWith("Bearer ")) {
                // Token desde header (aplicaciones web)
                token = authorization.replace("Bearer ", "");
            } else if (tokenParam != null) {
                // Token desde parámetro (aplicaciones móviles)
                token = tokenParam;
            } else {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token no proporcionado",
                    "message", "Debe proporcionar el token en el header Authorization o como parámetro 'token'"
                ));
            }
            
            // Revocar token usando JwtTokenProvider
            tokenProvider.revokeToken(token);
            boolean logoutSuccess = true;
            
            if (!logoutSuccess) {
                return ResponseEntity.status(401).body(Map.of(
                    "error", "No se pudo cerrar la sesión",
                    "message", "El token no es válido o ya fue revocado"
                ));
            }
            
            // Respuesta universal
            Map<String, String> response = Map.of(
                "message", "Sesión cerrada exitosamente",
                "status", "success",
                "note", "El token ha sido revocado y ya no es válido"
            );
            
            // Agregar redirección móvil si el token vino como parámetro
            if (tokenParam != null) {
                return ResponseEntity.ok(Map.of(
                    "message", "Sesión cerrada exitosamente",
                    "status", "success",
                    "mobile_redirect", "flowliteapp://auth/logout?status=success&message=Sesión%20cerrada%20exitosamente",
                    "note", "Las aplicaciones móviles reciben la confirmación a través del URL scheme personalizado"
                ));
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Error al cerrar sesión",
                "message", e.getMessage()
            ));
        }
    }

    @GetMapping("/validate")
    @Operation(summary = "Validar token JWT", 
               description = "Verifica si un token JWT es válido y no está revocado. " +
                           "Útil para verificar el estado de un token antes de usarlo. " +
                           "Consulta Redis para verificar si el token está en la blacklist.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Token válido y activo",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"valid\":true,\"revoked\":false,\"message\":\"Token válido y activo\",\"status\":\"active\",\"username\":\"johndoe\",\"userId\":\"123e4567-e89b-12d3-a456-426614174000\",\"note\":\"Token puede ser usado para autenticación\"}"
                    ))),
            @ApiResponse(responseCode = "401", description = "Token inválido o revocado",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"valid\":false,\"revoked\":true,\"message\":\"Token revocado - no puede ser usado\",\"status\":\"revoked\"}"
                    ))),
            @ApiResponse(responseCode = "400", description = "Error en la validación",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"valid\":false,\"revoked\":false,\"message\":\"Error al validar token: Token malformado\",\"status\":\"error\"}"
                    )))
    })
    public ResponseEntity<Map<String, Object>> validateToken(@RequestParam String token) {
        try {
            // Verificar si el token está revocado
            boolean isRevoked = tokenProvider.isTokenRevoked(token);
            
            if (isRevoked) {
                return ResponseEntity.status(401).body(Map.of(
                    "valid", false,
                    "revoked", true,
                    "message", "Token revocado - no puede ser usado",
                    "status", "revoked"
                ));
            }
            
            // Verificar si el token es válido (no expirado, firma correcta)
            boolean isValid = tokenProvider.validateToken(token);
            
            if (!isValid) {
                return ResponseEntity.status(401).body(Map.of(
                    "valid", false,
                    "revoked", false,
                    "message", "Token inválido - expirado o malformado",
                    "status", "invalid"
                ));
            }
            
            // Token válido y no revocado
            String username = tokenProvider.getUserNameFromToken(token);
            String userId = tokenProvider.getUserIdFromToken(token);
            
            return ResponseEntity.ok(Map.of(
                "valid", true,
                "revoked", false,
                "message", "Token válido y activo",
                "status", "active",
                "username", username,
                "userId", userId,
                "note", "Token puede ser usado para autenticación"
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "valid", false,
                "revoked", false,
                "message", "Error al validar token: " + e.getMessage(),
                "status", "error"
            ));
        }
    }

    @GetMapping("/me")
    @Operation(summary = "Obtener información del usuario autenticado", 
               description = "Devuelve la información del usuario basada en el token JWT proporcionado. " +
                           "Incluye ID, username, email y estado del token. " +
                           "Funciona para aplicaciones web (header Authorization) y móviles (parámetro token).")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Información del usuario obtenida",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"userId\":\"123e4567-e89b-12d3-a456-426614174000\",\"username\":\"johndoe\",\"tokenStatus\":\"active\",\"message\":\"Información del usuario obtenida exitosamente\"}"
                    ))),
            @ApiResponse(responseCode = "401", description = "Token inválido o revocado",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"error\":\"Token revocado\",\"message\":\"El token ha sido revocado y no puede ser usado\"}"
                    ))),
            @ApiResponse(responseCode = "400", description = "Token no proporcionado",
                    content = @Content(examples = @ExampleObject(
                            value = "{\"error\":\"Token no proporcionado\",\"message\":\"Debe proporcionar el token en el header Authorization o como parámetro 'token'\"}"
                    )))
    })
    public ResponseEntity<Map<String, Object>> getCurrentUser(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @RequestParam(value = "token", required = false) String tokenParam) {
        try {
            String token = null;
            
            // Determinar de dónde obtener el token
            if (authorization != null && authorization.startsWith("Bearer ")) {
                token = authorization.replace("Bearer ", "");
            } else if (tokenParam != null) {
                token = tokenParam;
            } else {
                return ResponseEntity.badRequest().body(Map.of(
                    "error", "Token no proporcionado",
                    "message", "Debe proporcionar el token en el header Authorization o como parámetro 'token'"
                ));
            }
            
            // Verificar si el token está revocado
            if (tokenProvider.isTokenRevoked(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "error", "Token revocado",
                    "message", "El token ha sido revocado y no puede ser usado"
                ));
            }
            
            // Verificar si el token es válido
            if (!tokenProvider.validateToken(token)) {
                return ResponseEntity.status(401).body(Map.of(
                    "error", "Token inválido",
                    "message", "El token es inválido o ha expirado"
                ));
            }
            
            // Extraer información del token
            String username = tokenProvider.getUserNameFromToken(token);
            String userId = tokenProvider.getUserIdFromToken(token);
            
            return ResponseEntity.ok(Map.of(
                "userId", userId,
                "username", username,
                "tokenStatus", "active",
                "message", "Información del usuario obtenida exitosamente"
            ));
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Error al obtener información del usuario",
                "message", e.getMessage()
            ));
        }
    }

}
