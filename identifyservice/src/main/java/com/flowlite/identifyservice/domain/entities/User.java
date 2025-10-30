package com.flowlite.identifyservice.domain.entities;
import com.flowlite.identifyservice.domain.valueobjects.Email;
import com.flowlite.identifyservice.domain.valueobjects.Password;
import com.flowlite.identifyservice.domain.valueobjects.Username;
import lombok.Data;
import lombok.Builder;

import java.util.Optional;

@Data
@Builder
public class User {

    private String id;
    private Username username;
    private Email email;
    private Password password;   // ahora puede ser null
    private Role role;
    private boolean active;

    public void deactivate() { this.active = false; }
    public void changeRole(Role newRole) { this.role = newRole; }

    // ✅ nuevo getter seguro
    public Optional<Password> getPassword() {
        return Optional.ofNullable(password);
    }

    // Getters adicionales para compatibilidad
    public Username getUsername() { return username; }
    public Email getEmail() { return email; }
    public String getId() { return id; }
    public Role getRole() { return role; }
    public boolean isActive() { return active; }
}