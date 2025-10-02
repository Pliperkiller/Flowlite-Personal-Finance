package com.flowlite.identifyservice.application.services;
import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.repositories.UserRepository;
import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;

import com.flowlite.identifyservice.application.ports.PasswordEncoder;
import com.flowlite.identifyservice.application.ports.TokenProvider;

@Service
@RequiredArgsConstructor
public class LoginUserService {

    private final UserRepository userRepository;
    private final TokenProvider tokenProvider;
    private final PasswordEncoder passwordEncoder;

    public String login(String username, String rawPassword) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("Usuario no encontrado"));

        // ✅ Validar que el usuario tenga contraseña
        String storedPassword = user.getPassword()
                .map(p -> p.getValue())
                .orElseThrow(() -> new IllegalStateException("El usuario no tiene contraseña local (probablemente login social)"));

        if (!passwordEncoder.matches(rawPassword, storedPassword)) {
            throw new IllegalArgumentException("Credenciales inválidas");
        }

        // Generar token
        return tokenProvider.generateToken(user);
    }
}
