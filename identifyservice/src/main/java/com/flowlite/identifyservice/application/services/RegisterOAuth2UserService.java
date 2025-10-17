package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.valueobjects.Username;
import com.flowlite.identifyservice.domain.valueobjects.Email;
import com.flowlite.identifyservice.domain.entities.Role;
import com.flowlite.identifyservice.domain.repositories.UserRepository;
import lombok.RequiredArgsConstructor;

import java.util.Optional;
import java.util.UUID;

import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RegisterOAuth2UserService {

    private final UserRepository userRepository;

    public User register(String email) {
        Optional<User> existingUser = userRepository.findByEmail(email);
        if (existingUser.isPresent()) {
            return existingUser.get();
        }

        User newUser = User.builder()
                .id(UUID.randomUUID())
                .username(new Username(email)) // usamos email como username
                .email(new Email(email))
                .password(null) // 👈 explícito: sin contraseña (OAuth2)
                .role(Role.USER)
                .active(true)
                .build();

        return userRepository.save(newUser);
    }
}
