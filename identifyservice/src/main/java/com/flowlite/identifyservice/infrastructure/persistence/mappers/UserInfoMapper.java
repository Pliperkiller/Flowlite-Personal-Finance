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
                .userId(entity.getUserId())
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
                .tipoIdentificacion(createIdentificationType(entity.getTipoIdentificacionCode(), 
                                                           entity.getTipoIdentificacionDescription()))
                .genero(entity.getGenero())
                .estadoCivil(entity.getEstadoCivil())
                .ocupacion(entity.getOcupacion())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .activo(entity.isActivo())
                .build();
    }

    public static UserInfoEntity toEntity(UserInfo userInfo) {
        if (userInfo == null) {
            return null;
        }

        return UserInfoEntity.builder()
                .id(userInfo.getId())
                .userId(userInfo.getUserId())
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
                .tipoIdentificacionCode(userInfo.getTipoIdentificacion() != null ? 
                                      userInfo.getTipoIdentificacion().getCode() : null)
                .tipoIdentificacionDescription(userInfo.getTipoIdentificacion() != null ? 
                                             userInfo.getTipoIdentificacion().getDescription() : null)
                .genero(userInfo.getGenero())
                .estadoCivil(userInfo.getEstadoCivil())
                .ocupacion(userInfo.getOcupacion())
                .createdAt(userInfo.getCreatedAt())
                .updatedAt(userInfo.getUpdatedAt())
                .activo(userInfo.isActivo())
                .build();
    }

    private static IdentificationType createIdentificationType(String code, String description) {
        if (code == null || description == null) {
            return null;
        }
        return new IdentificationType(code, description);
    }
}
