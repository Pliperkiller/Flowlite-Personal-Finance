package com.flowlite.identifyservice.infrastructure.security.oauth2;

import com.flowlite.identifyservice.application.services.RegisterUserService;
import com.flowlite.identifyservice.domain.entities.User;
import com.flowlite.identifyservice.domain.repositories.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.UUID;


@Component
@RequiredArgsConstructor
public class OAuth2UserServiceAdapter extends DefaultOAuth2UserService {

    private final UserRepository userRepository;
    private final RegisterUserService registerUserService; // 👈 caso de uso de aplicación

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) {
        // Delegamos a la implementación por defecto de Spring
        OAuth2User oAuth2User = super.loadUser(userRequest);

        // Extraer info básica (ejemplo con Google)
        String email = oAuth2User.getAttribute("email");
        String name = oAuth2User.getAttribute("name");

        // Buscar si ya existe en tu dominio
        Optional<User> existingUser = userRepository.findByEmail(email);

        User domainUser;
            if (existingUser.isPresent()) {
                domainUser = existingUser.get();
            } else {
                domainUser = registerUserService.register(
                    name != null ? name : email.split("@")[0],
                    email,
                    UUID.randomUUID().toString() // password random
                );
            }


        // Retornamos el OAuth2User enriquecido (puedes envolverlo en un adaptador si lo necesitas)
        return oAuth2User;
    }
}

