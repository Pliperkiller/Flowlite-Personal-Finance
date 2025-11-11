package com.flowlite.identifyservice.infrastructure.persistence.mappers;

import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;
import com.flowlite.identifyservice.infrastructure.persistence.entities.TermsVersionEntity;

public class TermsVersionMapper {

    public static TermsVersion toDomain(TermsVersionEntity entity) {
        if (entity == null) {
            return null;
        }

        return TermsVersion.builder()
                .id(entity.getId())
                .versionNumber(entity.getVersionNumber())
                .type(entity.getType())
                .title(entity.getTitle())
                .contentText(entity.getContentText())
                .contentUrl(entity.getContentUrl())
                .changeSummary(entity.getChangeSummary())
                .isMajorChange(entity.getIsMajorChange() != null ? entity.getIsMajorChange() : false)
                .requiresReacceptance(entity.getRequiresReacceptance() != null ? entity.getRequiresReacceptance() : false)
                .status(mapToTermsStatus(entity.getStatus()))
                .effectiveDate(entity.getEffectiveDate())
                .createdAt(entity.getCreatedAt())
                .publishedAt(entity.getPublishedAt())
                .supersededAt(entity.getSupersededAt())
                .createdBy(entity.getCreatedBy())
                .previousVersionId(entity.getPreviousVersionId())
                .active(entity.getActive() != null ? entity.getActive() : true)
                .build();
    }

    public static TermsVersionEntity toEntity(TermsVersion domain) {
        if (domain == null) {
            return null;
        }

        return TermsVersionEntity.builder()
                .id(domain.getId())
                .versionNumber(domain.getVersionNumber())
                .type(domain.getType())
                .title(domain.getTitle())
                .contentText(domain.getContentText())
                .contentUrl(domain.getContentUrl())
                .changeSummary(domain.getChangeSummary())
                .isMajorChange(domain.isMajorChange())
                .requiresReacceptance(domain.isRequiresReacceptance())
                .status(mapToTermsStatusEnum(domain.getStatus()))
                .effectiveDate(domain.getEffectiveDate())
                .createdAt(domain.getCreatedAt())
                .publishedAt(domain.getPublishedAt())
                .supersededAt(domain.getSupersededAt())
                .createdBy(domain.getCreatedBy())
                .previousVersionId(domain.getPreviousVersionId())
                .active(domain.isActive())
                .build();
    }

    private static TermsStatus mapToTermsStatus(TermsVersionEntity.TermsStatusEnum entityStatus) {
        if (entityStatus == null) {
            return TermsStatus.DRAFT;
        }

        return switch (entityStatus) {
            case DRAFT -> TermsStatus.DRAFT;
            case ACTIVE -> TermsStatus.ACTIVE;
            case SUPERSEDED -> TermsStatus.SUPERSEDED;
            case ARCHIVED -> TermsStatus.ARCHIVED;
        };
    }

    private static TermsVersionEntity.TermsStatusEnum mapToTermsStatusEnum(TermsStatus domainStatus) {
        if (domainStatus == null) {
            return TermsVersionEntity.TermsStatusEnum.DRAFT;
        }

        return switch (domainStatus) {
            case DRAFT -> TermsVersionEntity.TermsStatusEnum.DRAFT;
            case ACTIVE -> TermsVersionEntity.TermsStatusEnum.ACTIVE;
            case SUPERSEDED -> TermsVersionEntity.TermsStatusEnum.SUPERSEDED;
            case ARCHIVED -> TermsVersionEntity.TermsStatusEnum.ARCHIVED;
        };
    }
}
