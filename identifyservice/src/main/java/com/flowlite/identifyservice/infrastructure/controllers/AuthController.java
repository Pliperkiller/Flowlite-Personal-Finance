package com.flowlite.identifyservice.infrastructure.controllers;

import com.flowlite.identifyservice.application.services.LoginUserService;
import com.flowlite.identifyservice.application.services.RegisterUserService;
import com.flowlite.identifyservice.domain.entities.User;
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
@Tag(name = "Authentication", description = "Endpoints para autenticación tradicional (registro y login)")
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
               description = "Endpoint al que se redirige después de una autenticación OAuth2 exitosa. " +
                           "Recibe el token como parámetro de consulta para que las aplicaciones móviles puedan capturarlo.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Página de éxito mostrada correctamente"),
            @ApiResponse(responseCode = "400", description = "Token no proporcionado")
    })
    public ResponseEntity<Map<String, String>> oauth2Success(@RequestParam String token) {
        return ResponseEntity.ok(Map.of(
            "message", "Autenticación OAuth2 exitosa",
            "access_token", token,
            "note", "Este endpoint es usado para aplicaciones móviles que necesitan capturar el token"
        ));
    }

    @GetMapping("/error")
    @Operation(summary = "Página de error de autenticación OAuth2", 
               description = "Endpoint al que se redirige cuando ocurre un error durante la autenticación OAuth2.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "400", description = "Error en la autenticación OAuth2")
    })
    public ResponseEntity<Map<String, String>> oauth2Error(@RequestParam(required = false) String message) {
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Error en la autenticación OAuth2",
            "message", message != null ? message : "Error desconocido",
            "note", "Contacte al administrador si el problema persiste"
        ));
    }
}
