package com.flowlite.identifyservice.domain.entities;

import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entidad que almacena la información personal del usuario
 * Mantiene una relación uno a uno con User
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(of = "id")
@ToString(exclude = {"createdAt", "updatedAt"})
public class UserInfo {
    
    UUID id;
    UUID userId; // Referencia al User asociado
    
    // Información personal básica
    String primerNombre;
    String segundoNombre; // Opcional
    String primerApellido;
    String segundoApellido;
    String telefono;
    String direccion;
    String ciudad;
    String departamento;
    String pais;
    LocalDate fechaNacimiento;
    
    // Información de identificación
    String numeroIdentificacion;
    IdentificationType tipoIdentificacion;
    
    // Información adicional
    String genero;
    String estadoCivil;
    String ocupacion;
    
    // Metadatos
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
    boolean activo;
    
    // Métodos de utilidad
    public String getNombreCompleto() {
        StringBuilder nombreCompleto = new StringBuilder();
        
        if (primerNombre != null && !primerNombre.trim().isEmpty()) {
            nombreCompleto.append(primerNombre.trim());
        }
        
        if (segundoNombre != null && !segundoNombre.trim().isEmpty()) {
            nombreCompleto.append(" ").append(segundoNombre.trim());
        }
        
        if (primerApellido != null && !primerApellido.trim().isEmpty()) {
            nombreCompleto.append(" ").append(primerApellido.trim());
        }
        
        if (segundoApellido != null && !segundoApellido.trim().isEmpty()) {
            nombreCompleto.append(" ").append(segundoApellido.trim());
        }
        
        return nombreCompleto.toString().trim();
    }
    
    public void actualizarInformacion(String primerNombre, String segundoNombre, String primerApellido, 
                                    String segundoApellido, String telefono, String direccion, 
                                    String ciudad, String departamento) {
        this.primerNombre = primerNombre;
        this.segundoNombre = segundoNombre;
        this.primerApellido = primerApellido;
        this.segundoApellido = segundoApellido;
        this.telefono = telefono;
        this.direccion = direccion;
        this.ciudad = ciudad;
        this.departamento = departamento;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void actualizarIdentificacion(String numeroIdentificacion, IdentificationType tipoIdentificacion) {
        this.numeroIdentificacion = numeroIdentificacion;
        this.tipoIdentificacion = tipoIdentificacion;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void desactivar() {
        this.activo = false;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void activar() {
        this.activo = true;
        this.updatedAt = LocalDateTime.now();
    }
    
    public boolean tieneInformacionCompleta() {
        return primerNombre != null && !primerNombre.trim().isEmpty() &&
               primerApellido != null && !primerApellido.trim().isEmpty() &&
               telefono != null && !telefono.trim().isEmpty() &&
               numeroIdentificacion != null && !numeroIdentificacion.trim().isEmpty() &&
               tipoIdentificacion != null;
    }
}
