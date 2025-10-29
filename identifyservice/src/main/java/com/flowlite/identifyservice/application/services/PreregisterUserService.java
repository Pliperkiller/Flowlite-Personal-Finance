package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.application.ports.EmailService;
import com.flowlite.identifyservice.application.ports.PasswordEncoder;
import com.flowlite.identifyservice.application.ports.TokenProvider;
import com.flowlite.identifyservice.domain.entities.PendingUserData;
import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.entities.Role;
import com.flowlite.identifyservice.domain.valueobjects.Username;
import com.flowlite.identifyservice.domain.valueobjects.Email;
import com.flowlite.identifyservice.domain.valueobjects.Password;
import com.flowlite.identifyservice.infrastructure.persistence.redis.PendingUserRedisRepository;
import com.flowlite.identifyservice.domain.repositories.UserRepository;
import com.flowlite.identifyservice.infrastructure.dtos.PreregisterRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PreregisterUserService {
    
    private final PendingUserRedisRepository pendingUserRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final EmailService emailService;
    private final TokenProvider tokenProvider;
    private final ValidateTokenService validateTokenService;
    
    @Transactional
    public String preregister(PreregisterRequest request) {
        // Verificar si ya existe un usuario con ese email o username
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new IllegalArgumentException("El email ya está registrado");
        }
        
        if (userRepository.findByUsername(request.getUsername()).isPresent()) {
            throw new IllegalArgumentException("El nombre de usuario ya está en uso");
        }
        
        // Verificar si ya existe un preregistro pendiente
        if (pendingUserRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Ya existe un preregistro pendiente para este email");
        }
        
        if (pendingUserRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Ya existe un preregistro pendiente para este nombre de usuario");
        }
        
        // Crear token JWT de verificación
        String verificationToken = tokenProvider.generateVerificationToken(
            request.getUsername(), 
            request.getEmail()
        );
        
        // Encriptar contraseña
        String encryptedPassword = passwordEncoder.encode(request.getPassword());
        
        // Crear PendingUserData
        PendingUserData pendingUser = PendingUserData.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .password(encryptedPassword)
                .verificationToken(verificationToken)
                .tokenExpiration(LocalDateTime.now().plusHours(24)) // TTL para Redis
                .isVerified(false)
                .createdAt(LocalDateTime.now())
                .build();
        
        // Guardar en base de datos
        pendingUserRepository.save(pendingUser);
        
        // Enviar email de verificación
        emailService.sendVerificationEmail(request.getEmail(), verificationToken);
        
        return verificationToken;
    }
    
    @Transactional
    public User verifyAndRegister(String verificationToken) {
        // Validar JWT token usando el servicio existente
        if (!validateTokenService.isValid(verificationToken)) {
            throw new IllegalArgumentException("Token de verificación inválido");
        }
        
        // Verificar que sea un token de verificación
        if (!tokenProvider.isVerificationToken(verificationToken)) {
            throw new IllegalArgumentException("Token no es de verificación");
        }
        
        // Buscar datos en Redis
        PendingUserData pendingUser = pendingUserRepository.findByToken(verificationToken)
                .orElseThrow(() -> new IllegalArgumentException("Datos de preregistro no encontrados"));
        
        if (!pendingUser.canBeVerified()) {
            throw new IllegalArgumentException("Preregistro ya verificado o expirado");
        }
        
        // Crear usuario final
        User user = User.builder()
                .id(UUID.randomUUID().toString())
                .username(new Username(pendingUser.getUsername()))
                .email(new Email(pendingUser.getEmail()))
                .password(new Password(pendingUser.getPassword()))
                .role(Role.USER)
                .active(true)
                .build();
        
        // Guardar usuario final
        User savedUser = userRepository.save(user);
        
        // Eliminar PendingUserData de Redis
        pendingUserRepository.deleteByToken(verificationToken);
        
        return savedUser;
    }
    
    // Método para limpiar tokens expirados (opcional, Redis maneja TTL automáticamente)
    public void cleanupExpiredPendingUsers() {
        // Redis maneja automáticamente la expiración con TTL
        // Este método se mantiene por compatibilidad pero no es necesario
        // Los tokens expiran automáticamente después de 24 horas
    }
}
