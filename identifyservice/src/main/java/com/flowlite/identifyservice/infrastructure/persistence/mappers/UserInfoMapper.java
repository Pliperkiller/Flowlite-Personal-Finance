package com.flowlite.identifyservice.infrastructure.persistence.mappers;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import com.flowlite.identifyservice.infrastructure.persistence.entities.UserInfoEntity;

public class UserInfoMapper {

    public static UserInfo toDomain(UserInfoEntity entity) {
        if (entity == null) {
            return null;
        }

        return UserInfo.builder()
                .id(entity.getId())
                .userId(entity.getIdUser())
                .primerNombre(entity.getPrimerNombre())
                .segundoNombre(entity.getSegundoNombre())
                .primerApellido(entity.getPrimerApellido())
                .segundoApellido(entity.getSegundoApellido())
                .telefono(entity.getTelefono())
                .direccion(entity.getDireccion())
                .ciudad(entity.getCiudad())
                .departamento(entity.getDepartamento())
                .pais(entity.getPais())
                .fechaNacimiento(entity.getFechaNacimiento())
                .numeroIdentificacion(entity.getNumeroIdentificacion())
                .tipoIdentificacion(createIdentificationType(entity.getTipoIdentificacion()))
                .genero(entity.getGenero())
                .estadoCivil(entity.getEstadoCivil())
                .ocupacion(entity.getOcupacion())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .activo(entity.getActivo() != null ? entity.getActivo() : true)
                .build();
    }

    public static UserInfoEntity toEntity(UserInfo userInfo) {
        if (userInfo == null) {
            return null;
        }

        return UserInfoEntity.builder()
                .id(userInfo.getId())
                .idUser(userInfo.getUserId())
                .primerNombre(userInfo.getPrimerNombre())
                .segundoNombre(userInfo.getSegundoNombre())
                .primerApellido(userInfo.getPrimerApellido())
                .segundoApellido(userInfo.getSegundoApellido())
                .telefono(userInfo.getTelefono())
                .direccion(userInfo.getDireccion())
                .ciudad(userInfo.getCiudad())
                .departamento(userInfo.getDepartamento())
                .pais(userInfo.getPais())
                .fechaNacimiento(userInfo.getFechaNacimiento())
                .numeroIdentificacion(userInfo.getNumeroIdentificacion())
                .tipoIdentificacion(userInfo.getTipoIdentificacion() != null ?
                                  userInfo.getTipoIdentificacion().getCode() : null)
                .genero(userInfo.getGenero())
                .estadoCivil(userInfo.getEstadoCivil())
                .ocupacion(userInfo.getOcupacion())
                .createdAt(userInfo.getCreatedAt())
                .updatedAt(userInfo.getUpdatedAt())
                .activo(userInfo.isActivo())
                .build();
    }

    private static IdentificationType createIdentificationType(String code) {
        if (code == null) {
            return null;
        }

        // Mapear el código al IdentificationType correspondiente
        return switch (code) {
            case "CC" -> new IdentificationType("CC", "Cédula de Ciudadanía");
            case "CE" -> new IdentificationType("CE", "Cédula de Extranjería");
            case "PA" -> new IdentificationType("PA", "Pasaporte");
            case "TI" -> new IdentificationType("TI", "Tarjeta de Identidad");
            case "RC" -> new IdentificationType("RC", "Registro Civil");
            case "NIT" -> new IdentificationType("NIT", "Número de Identificación Tributaria");
            default -> new IdentificationType(code, code);
        };
    }
}
