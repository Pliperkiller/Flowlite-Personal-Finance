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
                .id(entity.getIdUser())
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
                .fechaNacimiento(null)  // No existe en el esquema actual
                .numeroIdentificacion(entity.getNumeroIdentificacion())
                .tipoIdentificacion(createIdentificationType(entity.getTipoIdentificacion(), entity.getTipoIdentificacion()))
                .genero(null)  // No existe en el esquema actual
                .estadoCivil(null)  // No existe en el esquema actual
                .ocupacion(null)  // No existe en el esquema actual
                .createdAt(null)  // No existe en el esquema actual
                .updatedAt(null)  // No existe en el esquema actual
                .activo(true)  // Por defecto true ya que no existe en el esquema actual
                .build();
    }

    public static UserInfoEntity toEntity(UserInfo userInfo) {
        if (userInfo == null) {
            return null;
        }

        return UserInfoEntity.builder()
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
                .numeroIdentificacion(userInfo.getNumeroIdentificacion())
                .tipoIdentificacion(userInfo.getTipoIdentificacion() != null ?
                                  userInfo.getTipoIdentificacion().getCode() : null)
                .build();
    }

    private static IdentificationType createIdentificationType(String code, String description) {
        if (code == null || description == null) {
            return null;
        }
        return new IdentificationType(code, description);
    }
}
