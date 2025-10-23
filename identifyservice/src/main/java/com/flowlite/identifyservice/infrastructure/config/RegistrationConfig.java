package com.flowlite.identifyservice.infrastructure.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConfigurationProperties(prefix = "app.registration")
public class RegistrationConfig {
    
    private boolean directEnabled = true;
    private boolean preregisterEnabled = true;
    private boolean oauth2Enabled = true;
    
    // Getters y Setters
    public boolean isDirectEnabled() {
        return directEnabled;
    }
    
    public void setDirectEnabled(boolean directEnabled) {
        this.directEnabled = directEnabled;
    }
    
    public boolean isPreregisterEnabled() {
        return preregisterEnabled;
    }
    
    public void setPreregisterEnabled(boolean preregisterEnabled) {
        this.preregisterEnabled = preregisterEnabled;
    }
    
    public boolean isOauth2Enabled() {
        return oauth2Enabled;
    }
    
    public void setOauth2Enabled(boolean oauth2Enabled) {
        this.oauth2Enabled = oauth2Enabled;
    }
}

