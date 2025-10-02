package com.flowlite.identifyservice.infrastructure.security.oauth2;

import com.flowlite.identifyservice.application.services.RegisterOAuth2UserService;
import com.flowlite.identifyservice.application.ports.TokenProvider;
import com.flowlite.identifyservice.domain.entities.User;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
@RequiredArgsConstructor
public class OAuth2LoginSuccessHandler implements AuthenticationSuccessHandler {

    private final RegisterOAuth2UserService registerOAuth2UserService;
    private final TokenProvider tokenProvider;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException {

        try {
            OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();
            String email = oAuth2User.getAttribute("email");
            
            System.out.println("OAuth2 Success - Email: " + email);
            
            User user = registerOAuth2UserService.register(email);
            System.out.println("User registered/found: " + user.getEmail());
            
            String jwt = tokenProvider.generateToken(user);
            System.out.println("JWT generated successfully");
            
            response.setContentType("application/json");
            response.getWriter().write("{\"access_token\":\"" + jwt + "\"}");
            System.out.println("Response sent successfully");
            
        } catch (Exception e) {
            System.err.println("Error in OAuth2LoginSuccessHandler: " + e.getMessage());
            e.printStackTrace();
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"Internal server error: " + e.getMessage() + "\"}");
        }
    }
}
