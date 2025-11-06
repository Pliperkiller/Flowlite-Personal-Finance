package com.flowlite.identifyservice.infrastructure.persistence.entities;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "UserInfo")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserInfoEntity {

    @Id
    @Column(name = "id", columnDefinition = "BINARY(16)")
    private UUID id;

    @Column(name = "id_user", columnDefinition = "BINARY(16)", nullable = false, unique = true)
    private UUID idUser;

    // Información personal básica
    @Column(name = "primerNombre", length = 50)
    private String primerNombre;

    @Column(name = "segundoNombre", length = 50)
    private String segundoNombre;

    @Column(name = "primerApellido", length = 50)
    private String primerApellido;

    @Column(name = "segundoApellido", length = 50)
    private String segundoApellido;

    @Column(name = "telefono", length = 15)
    private String telefono;

    @Column(name = "direccion", length = 200)
    private String direccion;

    @Column(name = "ciudad", length = 100)
    private String ciudad;

    @Column(name = "departamento", length = 100)
    private String departamento;

    @Column(name = "pais", length = 100)
    private String pais;

    @Column(name = "fechaNacimiento")
    private LocalDate fechaNacimiento;

    // Información de identificación
    @Column(name = "numeroIdentificacion", length = 20, unique = true)
    private String numeroIdentificacion;

    @Column(name = "tipoIdentificacion", length = 10)
    private String tipoIdentificacion;

    // Información adicional
    @Column(name = "genero", length = 20)
    private String genero;

    @Column(name = "estadoCivil", length = 30)
    private String estadoCivil;

    @Column(name = "ocupacion", length = 100)
    private String ocupacion;

    // Metadatos
    @Column(name = "createdAt", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updatedAt")
    private LocalDateTime updatedAt;

    @Column(name = "activo")
    private Boolean activo;

    @PrePersist
    protected void onCreate() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (activo == null) {
            activo = true;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
