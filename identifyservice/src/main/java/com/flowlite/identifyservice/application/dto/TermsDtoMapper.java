package com.flowlite.identifyservice.application.dto;

import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Mapper between Terms domain entities and DTOs
 */
public class TermsDtoMapper {

    /**
     * Maps TermsVersion domain entity to TermsVersionResponse DTO
     */
    public static TermsVersionResponse toTermsVersionResponse(TermsVersion domain) {
        if (domain == null) {
            return null;
        }

        return TermsVersionResponse.builder()
                .id(domain.getId())
                .versionNumber(domain.getVersionNumber())
                .type(domain.getType())
                .title(domain.getTitle())
                .contentText(domain.getContentText())
                .contentUrl(domain.getContentUrl())
                .changeSummary(domain.getChangeSummary())
                .isMajorChange(domain.isMajorChange())
                .requiresReacceptance(domain.isRequiresReacceptance())
                .status(domain.getStatus() != null ? domain.getStatus().name() : null)
                .effectiveDate(domain.getEffectiveDate())
                .createdAt(domain.getCreatedAt())
                .publishedAt(domain.getPublishedAt())
                .active(domain.isActive())
                .build();
    }

    /**
     * Maps CreateTermsVersionRequest DTO to TermsVersion domain entity
     */
    public static TermsVersion toTermsVersion(CreateTermsVersionRequest request) {
        if (request == null) {
            return null;
        }

        return TermsVersion.builder()
                .id(UUID.randomUUID())
                .versionNumber(request.getVersionNumber())
                .type(request.getType())
                .title(request.getTitle())
                .contentText(request.getContentText())
                .contentUrl(request.getContentUrl())
                .changeSummary(request.getChangeSummary())
                .isMajorChange(request.getIsMajorChange())
                .requiresReacceptance(request.getRequiresReacceptance())
                .status(TermsStatus.DRAFT)
                .effectiveDate(request.getEffectiveDate())
                .createdAt(LocalDateTime.now())
                .createdBy(request.getCreatedBy())
                .previousVersionId(request.getPreviousVersionId())
                .active(true)
                .build();
    }

    /**
     * Maps UserTermsAcceptance domain entity to TermsAcceptanceResponse DTO
     */
    public static TermsAcceptanceResponse toTermsAcceptanceResponse(
            UserTermsAcceptance acceptance,
            String versionNumber) {
        if (acceptance == null) {
            return null;
        }

        return TermsAcceptanceResponse.builder()
                .id(acceptance.getId())
                .userId(acceptance.getUserId())
                .termsVersionId(acceptance.getTermsVersionId())
                .versionNumber(versionNumber)
                .acceptanceType(acceptance.getAcceptanceType() != null ?
                    acceptance.getAcceptanceType().name() : null)
                .acceptedAt(acceptance.getAcceptedAt())
                .ipAddress(acceptance.getIpAddress())
                .acceptanceMethod(acceptance.getAcceptanceMethod())
                .acceptedFromCountry(acceptance.getAcceptedFromCountry())
                .verified(acceptance.isVerified())
                .active(acceptance.isActive())
                .build();
    }

    /**
     * Creates a TermsStatusResponse based on current and accepted versions
     */
    public static TermsStatusResponse toTermsStatusResponse(
            UUID userId,
            TermsVersion currentVersion,
            UserTermsAcceptance acceptance) {

        boolean needsAcceptance = acceptance == null ||
            (currentVersion != null && !currentVersion.getId().equals(acceptance.getTermsVersionId()));

        String message = needsAcceptance ?
            "You need to accept the latest terms and conditions" :
            "You are up to date with the latest terms";

        return TermsStatusResponse.builder()
                .userId(userId)
                .currentTermsVersionId(currentVersion != null ? currentVersion.getId() : null)
                .currentVersionNumber(currentVersion != null ? currentVersion.getVersionNumber() : null)
                .acceptedTermsVersionId(acceptance != null ? acceptance.getTermsVersionId() : null)
                .acceptedVersionNumber(null) // Will be populated by service if needed
                .needsAcceptance(needsAcceptance)
                .requiresReacceptance(currentVersion != null && currentVersion.isRequiresReacceptance())
                .isMajorChange(currentVersion != null && currentVersion.isMajorChange())
                .acceptedAt(acceptance != null ? acceptance.getAcceptedAt() : null)
                .changeSummary(currentVersion != null ? currentVersion.getChangeSummary() : null)
                .message(message)
                .build();
    }
}
