package com.flowlite.identifyservice.application.services;

import org.springframework.stereotype.Service;

import com.flowlite.identifyservice.application.ports.TokenProvider;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ValidateTokenService {

    private final TokenProvider tokenProvider;

    public boolean isValid(String token) {
        return tokenProvider.validateToken(token);
    }
}
