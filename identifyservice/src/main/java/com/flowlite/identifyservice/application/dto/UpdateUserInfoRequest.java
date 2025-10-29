package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

/**
 * DTO para la actualización de información personal del usuario
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Solicitud para actualizar información personal del usuario")
public class UpdateUserInfoRequest {

    @NotBlank(message = "El primer nombre es obligatorio")
    @Size(min = 2, max = 50, message = "El primer nombre debe tener entre 2 y 50 caracteres")
    @Schema(description = "Primer nombre del usuario", example = "Juan", required = true)
    String primerNombre;

    @Size(max = 50, message = "El segundo nombre no puede exceder 50 caracteres")
    @Schema(description = "Segundo nombre del usuario (opcional)", example = "Carlos")
    String segundoNombre;

    @NotBlank(message = "El primer apellido es obligatorio")
    @Size(min = 2, max = 50, message = "El primer apellido debe tener entre 2 y 50 caracteres")
    @Schema(description = "Primer apellido del usuario", example = "García", required = true)
    String primerApellido;

    @Size(max = 50, message = "El segundo apellido no puede exceder 50 caracteres")
    @Schema(description = "Segundo apellido del usuario (opcional)", example = "López")
    String segundoApellido;

    @NotBlank(message = "El teléfono es obligatorio")
    @Pattern(regexp = "^[0-9]{10,15}$", message = "El teléfono debe contener solo números y tener entre 10 y 15 dígitos")
    @Schema(description = "Número de teléfono del usuario", example = "3001234567", required = true)
    String telefono;

    @Size(max = 200, message = "La dirección no puede exceder 200 caracteres")
    @Schema(description = "Dirección del usuario", example = "Calle 123 #45-67")
    String direccion;

    @Size(max = 100, message = "La ciudad no puede exceder 100 caracteres")
    @Schema(description = "Ciudad del usuario", example = "Bogotá")
    String ciudad;

    @Size(max = 100, message = "El departamento no puede exceder 100 caracteres")
    @Schema(description = "Departamento del usuario", example = "Cundinamarca")
    String departamento;

    @Size(max = 100, message = "El país no puede exceder 100 caracteres")
    @Schema(description = "País del usuario", example = "Colombia")
    String pais;

    @Schema(description = "Fecha de nacimiento del usuario", example = "1990-05-15")
    LocalDate fechaNacimiento;

    @NotBlank(message = "El número de identificación es obligatorio")
    @Pattern(regexp = "^[0-9]{6,20}$", message = "El número de identificación debe contener solo números y tener entre 6 y 20 dígitos")
    @Schema(description = "Número de identificación del usuario", example = "12345678", required = true)
    String numeroIdentificacion;

    @NotNull(message = "El tipo de identificación es obligatorio")
    @Schema(description = "Tipo de identificación del usuario", example = "CC", required = true)
    String tipoIdentificacion;

    @Size(max = 20, message = "El género no puede exceder 20 caracteres")
    @Schema(description = "Género del usuario", example = "Masculino")
    String genero;

    @Size(max = 30, message = "El estado civil no puede exceder 30 caracteres")
    @Schema(description = "Estado civil del usuario", example = "Soltero")
    String estadoCivil;

    @Size(max = 100, message = "La ocupación no puede exceder 100 caracteres")
    @Schema(description = "Ocupación del usuario", example = "Ingeniero")
    String ocupacion;
}
