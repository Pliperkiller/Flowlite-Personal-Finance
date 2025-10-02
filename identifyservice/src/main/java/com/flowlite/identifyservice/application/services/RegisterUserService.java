package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.application.ports.PasswordEncoder;
import com.flowlite.identifyservice.domain.entities.Role;
import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.valueobjects.Email;
import com.flowlite.identifyservice.domain.valueobjects.Password;
import com.flowlite.identifyservice.domain.valueobjects.Username;
import com.flowlite.identifyservice.domain.repositories.UserRepository;



import lombok.RequiredArgsConstructor;

import java.util.UUID;

import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RegisterUserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public User register(String username, String email, String rawPassword) {
        // Validar que no exista usuario con el mismo email o username
        userRepository.findByEmail(email).ifPresent(u -> {
            throw new IllegalArgumentException("El email ya está registrado");
        });

        userRepository.findByUsername(username).ifPresent(u -> {
            throw new IllegalArgumentException("El username ya está en uso");
        });

        // Hash de password (aquí llamarías un PasswordEncoder, desde dominio solo validación)
        String hashedPassword = passwordEncoder.encode(rawPassword); // esto es un String

        User newUser = User.builder()
        .id(UUID.randomUUID())
        .username(new Username(username))
        .email(new Email(email))
        .password(new Password(hashedPassword))
        .role(Role.USER)
        .active(true)
        .build();

        return userRepository.save(newUser);
    }
}