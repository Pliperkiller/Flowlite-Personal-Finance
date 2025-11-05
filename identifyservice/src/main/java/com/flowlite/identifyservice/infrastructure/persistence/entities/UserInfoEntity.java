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
    private UUID id;

    @Column(name = "user_id", nullable = false, unique = true)
    private UUID userId;

    // Información personal básica
    @Column(name = "primer_nombre")
    private String primerNombre;

    @Column(name = "segundo_nombre")
    private String segundoNombre;

    @Column(name = "primer_apellido")
    private String primerApellido;

    @Column(name = "segundo_apellido")
    private String segundoApellido;

    @Column(name = "telefono")
    private String telefono;

    @Column(name = "direccion")
    private String direccion;

    @Column(name = "ciudad")
    private String ciudad;

    @Column(name = "departamento")
    private String departamento;

    @Column(name = "pais")
    private String pais;

    @Column(name = "fecha_nacimiento")
    private LocalDate fechaNacimiento;

    // Información de identificación
    @Column(name = "numero_identificacion")
    private String numeroIdentificacion;

    @Column(name = "tipo_identificacion_code")
    private String tipoIdentificacionCode;

    @Column(name = "tipo_identificacion_description")
    private String tipoIdentificacionDescription;

    // Información adicional
    @Column(name = "genero")
    private String genero;

    @Column(name = "estado_civil")
    private String estadoCivil;

    @Column(name = "ocupacion")
    private String ocupacion;

    // Metadatos
    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "activo")
    private boolean activo;
}
