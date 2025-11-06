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
    @Column(name = "id_user")
    private UUID idUser;

    // Información personal básica
    @Column(name = "primerNombre")
    private String primerNombre;

    @Column(name = "segundoNombre")
    private String segundoNombre;

    @Column(name = "primerApellido")
    private String primerApellido;

    @Column(name = "segundoApellido")
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

    // Información de identificación
    @Column(name = "numeroIdentificacion")
    private String numeroIdentificacion;

    @Column(name = "tipoIdentificacion")
    private String tipoIdentificacion;
}
