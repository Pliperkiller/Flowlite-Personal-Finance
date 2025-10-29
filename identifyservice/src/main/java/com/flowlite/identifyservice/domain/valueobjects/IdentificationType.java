package com.flowlite.identifyservice.domain.valueobjects;

import lombok.Value;

/**
 * Value Object que representa los tipos de identificación utilizados en Colombia
 */
@Value
public class IdentificationType {
    
    String code;
    String description;
    
    public IdentificationType(String code, String description) {
        if (code == null || code.trim().isEmpty()) {
            throw new IllegalArgumentException("El código del tipo de identificación no puede ser nulo o vacío");
        }
        if (description == null || description.trim().isEmpty()) {
            throw new IllegalArgumentException("La descripción del tipo de identificación no puede ser nula o vacía");
        }
        this.code = code.trim().toUpperCase();
        this.description = description.trim();
    }
    
    // Métodos estáticos para crear instancias de los tipos comunes
    public static IdentificationType cedulaCiudadania() {
        return new IdentificationType("CC", "Cédula de Ciudadanía");
    }
    
    public static IdentificationType cedulaExtranjeria() {
        return new IdentificationType("CE", "Cédula de Extranjería");
    }
    
    public static IdentificationType pasaporte() {
        return new IdentificationType("PA", "Pasaporte");
    }
    
    public static IdentificationType tarjetaIdentidad() {
        return new IdentificationType("TI", "Tarjeta de Identidad");
    }
    
    public static IdentificationType registroCivil() {
        return new IdentificationType("RC", "Registro Civil");
    }
    
    public static IdentificationType nit() {
        return new IdentificationType("NIT", "NIT");
    }
    
    // Método para crear desde string
    public static IdentificationType fromCode(String code) {
        if (code == null) {
            throw new IllegalArgumentException("El código no puede ser nulo");
        }
        
        String upperCode = code.trim().toUpperCase();
        switch (upperCode) {
            case "CC":
                return cedulaCiudadania();
            case "CE":
                return cedulaExtranjeria();
            case "PA":
                return pasaporte();
            case "TI":
                return tarjetaIdentidad();
            case "RC":
                return registroCivil();
            case "NIT":
                return nit();
            default:
                throw new IllegalArgumentException("Tipo de identificación no válido: " + code);
        }
    }
    
    @Override
    public String toString() {
        return description;
    }
}
