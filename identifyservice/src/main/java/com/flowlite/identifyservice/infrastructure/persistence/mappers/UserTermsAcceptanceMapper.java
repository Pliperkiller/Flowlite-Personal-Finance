package com.flowlite.identifyservice.infrastructure.persistence.mappers;

import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;
import com.flowlite.identifyservice.infrastructure.persistence.entities.UserTermsAcceptanceEntity;

public class UserTermsAcceptanceMapper {

    public static UserTermsAcceptance toDomain(UserTermsAcceptanceEntity entity) {
        if (entity == null) {
            return null;
        }

        return UserTermsAcceptance.builder()
                .id(entity.getId())
                .userId(entity.getUserId())
                .termsVersionId(entity.getTermsVersionId())
                .acceptedAt(entity.getAcceptedAt())
                .acceptanceType(mapToAcceptanceType(entity.getAcceptanceType()))
                .ipAddress(entity.getIpAddress())
                .userAgent(entity.getUserAgent())
                .acceptanceMethod(entity.getAcceptanceMethod())
                .acceptedFromCountry(entity.getAcceptedFromCountry())
                .acceptedFromCity(entity.getAcceptedFromCity())
                .verified(entity.getVerified() != null ? entity.getVerified() : false)
                .verifiedAt(entity.getVerifiedAt())
                .createdAt(entity.getCreatedAt())
                .active(entity.getActive() != null ? entity.getActive() : true)
                .build();
    }

    public static UserTermsAcceptanceEntity toEntity(UserTermsAcceptance domain) {
        if (domain == null) {
            return null;
        }

        return UserTermsAcceptanceEntity.builder()
                .id(domain.getId())
                .userId(domain.getUserId())
                .termsVersionId(domain.getTermsVersionId())
                .acceptedAt(domain.getAcceptedAt())
                .acceptanceType(mapToAcceptanceTypeEnum(domain.getAcceptanceType()))
                .ipAddress(domain.getIpAddress())
                .userAgent(domain.getUserAgent())
                .acceptanceMethod(domain.getAcceptanceMethod())
                .acceptedFromCountry(domain.getAcceptedFromCountry())
                .acceptedFromCity(domain.getAcceptedFromCity())
                .verified(domain.isVerified())
                .verifiedAt(domain.getVerifiedAt())
                .createdAt(domain.getCreatedAt())
                .active(domain.isActive())
                .build();
    }

    private static AcceptanceType mapToAcceptanceType(UserTermsAcceptanceEntity.AcceptanceTypeEnum entityType) {
        if (entityType == null) {
            return AcceptanceType.INITIAL_SIGNUP;
        }

        return switch (entityType) {
            case INITIAL_SIGNUP -> AcceptanceType.INITIAL_SIGNUP;
            case FORCED_UPDATE -> AcceptanceType.FORCED_UPDATE;
            case OPTIONAL_UPDATE -> AcceptanceType.OPTIONAL_UPDATE;
            case REACTIVATION -> AcceptanceType.REACTIVATION;
        };
    }

    private static UserTermsAcceptanceEntity.AcceptanceTypeEnum mapToAcceptanceTypeEnum(AcceptanceType domainType) {
        if (domainType == null) {
            return UserTermsAcceptanceEntity.AcceptanceTypeEnum.INITIAL_SIGNUP;
        }

        return switch (domainType) {
            case INITIAL_SIGNUP -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.INITIAL_SIGNUP;
            case FORCED_UPDATE -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.FORCED_UPDATE;
            case OPTIONAL_UPDATE -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.OPTIONAL_UPDATE;
            case REACTIVATION -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.REACTIVATION;
        };
    }
}
