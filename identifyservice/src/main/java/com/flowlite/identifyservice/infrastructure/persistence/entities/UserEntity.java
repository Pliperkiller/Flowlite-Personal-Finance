package com.flowlite.identifyservice.infrastructure.persistence.entities;

import com.flowlite.identifyservice.domain.entities.Role;
import lombok.*;

import jakarta.persistence.*;

@Entity
@Table(name = "User")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserEntity {

    @Id
    @Column(name = "id_user", columnDefinition = "CHAR(36)")
    private String idUser;

    @Column(name = "username", nullable = false, length = 100)
    private String username;

    @Column(name = "email", nullable = false, unique = true, length = 255)
    private String email;

    @Column(name = "password", nullable = false, length = 255)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", length = 50)
    private Role role;

    @Column(name = "active")
    private boolean active;
}
