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
                .firstName(entity.getFirstName())
                .middleName(entity.getMiddleName())
                .lastName(entity.getLastName())
                .secondLastName(entity.getSecondLastName())
                .phone(entity.getPhone())
                .address(entity.getAddress())
                .city(entity.getCity())
                .state(entity.getState())
                .country(entity.getCountry())
                .birthDate(entity.getBirthDate())
                .identificationNumber(entity.getIdentificationNumber())
                .identificationType(createIdentificationType(entity.getIdentificationType()))
                .gender(entity.getGender())
                .maritalStatus(entity.getMaritalStatus())
                .occupation(entity.getOccupation())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .active(entity.getActive() != null ? entity.getActive() : true)
                .build();
    }

    public static UserInfoEntity toEntity(UserInfo userInfo) {
        if (userInfo == null) {
            return null;
        }

        return UserInfoEntity.builder()
                .id(userInfo.getId())
                .userId(userInfo.getUserId())
                .firstName(userInfo.getFirstName())
                .middleName(userInfo.getMiddleName())
                .lastName(userInfo.getLastName())
                .secondLastName(userInfo.getSecondLastName())
                .phone(userInfo.getPhone())
                .address(userInfo.getAddress())
                .city(userInfo.getCity())
                .state(userInfo.getState())
                .country(userInfo.getCountry())
                .birthDate(userInfo.getBirthDate())
                .identificationNumber(userInfo.getIdentificationNumber())
                .identificationType(userInfo.getIdentificationType() != null ?
                                  userInfo.getIdentificationType().getCode() : null)
                .gender(userInfo.getGender())
                .maritalStatus(userInfo.getMaritalStatus())
                .occupation(userInfo.getOccupation())
                .createdAt(userInfo.getCreatedAt())
                .updatedAt(userInfo.getUpdatedAt())
                .active(userInfo.isActive())
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
