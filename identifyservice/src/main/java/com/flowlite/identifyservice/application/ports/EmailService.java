package com.flowlite.identifyservice.application.ports;

public interface EmailService {
    void sendVerificationEmail(String email, String verificationToken);
    void sendWelcomeEmail(String email, String username);
}

