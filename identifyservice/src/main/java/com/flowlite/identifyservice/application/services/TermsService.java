package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.repositories.TermsVersionRepository;
import com.flowlite.identifyservice.domain.repositories.UserTermsAcceptanceRepository;
import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;
import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;
import lombok.*;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Service for managing Terms and Conditions versioning and user acceptance
 */
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@Slf4j
public class TermsService {

    TermsVersionRepository termsVersionRepository;
    UserTermsAcceptanceRepository userTermsAcceptanceRepository;

    /**
     * Creates a new terms version (Admin function)
     */
    @Transactional
    public TermsVersion createTermsVersion(@NonNull TermsVersion termsVersion) {
        log.info("Creating new terms version: {}", termsVersion.getVersionNumber());

        // Validate that version number doesn't exist
        if (termsVersionRepository.existsByVersionNumber(termsVersion.getVersionNumber())) {
            throw new IllegalArgumentException("Version number already exists: " + termsVersion.getVersionNumber());
        }

        // Save as DRAFT initially
        termsVersion.setStatus(TermsStatus.DRAFT);

        return termsVersionRepository.save(termsVersion);
    }

    /**
     * Publishes a terms version (makes it active)
     */
    @Transactional
    public TermsVersion publishTermsVersion(@NonNull UUID termsVersionId) {
        log.info("Publishing terms version: {}", termsVersionId);

        TermsVersion termsVersion = termsVersionRepository.findById(termsVersionId)
                .orElseThrow(() -> new IllegalArgumentException("Terms version not found"));

        // Supersede current active version of the same type
        Optional<TermsVersion> currentActive = termsVersionRepository.findActiveByType(termsVersion.getType());
        if (currentActive.isPresent()) {
            TermsVersion oldVersion = currentActive.get();
            oldVersion.supersede();
            termsVersionRepository.save(oldVersion);
            log.info("Superseded previous version: {}", oldVersion.getVersionNumber());
        }

        // Activate new version
        termsVersion.activate();
        return termsVersionRepository.save(termsVersion);
    }

    /**
     * Gets the current active terms version by type
     */
    public Optional<TermsVersion> getCurrentTermsVersion(@NonNull String type) {
        return termsVersionRepository.findActiveByType(type);
    }

    /**
     * Gets a specific terms version by ID
     */
    public Optional<TermsVersion> getTermsVersion(@NonNull UUID versionId) {
        return termsVersionRepository.findById(versionId);
    }

    /**
     * Gets terms version history by type
     */
    public List<TermsVersion> getTermsHistory(@NonNull String type) {
        return termsVersionRepository.findHistoryByType(type);
    }

    /**
     * Records user acceptance of terms
     */
    @Transactional
    public UserTermsAcceptance acceptTerms(
            @NonNull UUID userId,
            @NonNull UUID termsVersionId,
            @NonNull AcceptanceType acceptanceType,
            String ipAddress,
            String userAgent,
            String acceptanceMethod,
            String country,
            String city) {

        log.info("User {} accepting terms version {}", userId, termsVersionId);

        // Validate terms version exists and is active
        TermsVersion termsVersion = termsVersionRepository.findById(termsVersionId)
                .orElseThrow(() -> new IllegalArgumentException("Terms version not found"));

        if (!termsVersion.isCurrentlyActive()) {
            throw new IllegalArgumentException("Cannot accept inactive terms version");
        }

        // Check if user already accepted this version
        Optional<UserTermsAcceptance> existing = userTermsAcceptanceRepository
                .findByUserIdAndTermsVersionId(userId, termsVersionId);

        if (existing.isPresent() && existing.get().isActive()) {
            log.warn("User {} already accepted terms version {}", userId, termsVersionId);
            return existing.get();
        }

        // Create acceptance record
        UserTermsAcceptance acceptance = UserTermsAcceptance.createAcceptance(
                userId,
                termsVersionId,
                acceptanceType,
                ipAddress,
                userAgent,
                acceptanceMethod
        );

        acceptance.setAcceptedFromCountry(country);
        acceptance.setAcceptedFromCity(city);

        UserTermsAcceptance saved = userTermsAcceptanceRepository.save(acceptance);
        log.info("User {} successfully accepted terms version {}", userId, termsVersionId);

        return saved;
    }

    /**
     * Checks if user needs to accept new terms
     */
    public boolean userNeedsToAcceptTerms(@NonNull UUID userId, @NonNull String termsType) {
        // Get current active version
        Optional<TermsVersion> currentVersion = termsVersionRepository.findActiveByType(termsType);
        if (currentVersion.isEmpty()) {
            return false; // No active terms to accept
        }

        // Check if user has accepted the current version
        return !userTermsAcceptanceRepository.hasUserAcceptedVersion(userId, currentVersion.get().getId());
    }

    /**
     * Gets user's latest acceptance for a terms type
     */
    public Optional<UserTermsAcceptance> getUserLatestAcceptance(@NonNull UUID userId, @NonNull String termsType) {
        return userTermsAcceptanceRepository.findLatestByUserIdAndTermsType(userId, termsType);
    }

    /**
     * Gets all user's acceptances
     */
    public List<UserTermsAcceptance> getUserAcceptanceHistory(@NonNull UUID userId) {
        return userTermsAcceptanceRepository.findAllActiveByUserId(userId);
    }

    /**
     * Gets statistics for a terms version (how many users accepted)
     */
    public long getAcceptanceCount(@NonNull UUID termsVersionId) {
        return userTermsAcceptanceRepository.countByTermsVersionId(termsVersionId);
    }

    /**
     * Gets users who need to accept new terms
     */
    public List<UUID> getUsersNeedingAcceptance(@NonNull UUID termsVersionId) {
        return userTermsAcceptanceRepository.findUserIdsWithoutLatestAcceptance(termsVersionId);
    }

    /**
     * Verifies a user's acceptance (e.g., after email confirmation)
     */
    @Transactional
    public UserTermsAcceptance verifyAcceptance(@NonNull UUID acceptanceId) {
        UserTermsAcceptance acceptance = userTermsAcceptanceRepository.findById(acceptanceId)
                .orElseThrow(() -> new IllegalArgumentException("Acceptance not found"));

        acceptance.verify();
        return userTermsAcceptanceRepository.save(acceptance);
    }

    /**
     * Archives old terms version (soft delete)
     */
    @Transactional
    public void archiveTermsVersion(@NonNull UUID termsVersionId) {
        log.info("Archiving terms version: {}", termsVersionId);

        TermsVersion termsVersion = termsVersionRepository.findById(termsVersionId)
                .orElseThrow(() -> new IllegalArgumentException("Terms version not found"));

        if (termsVersion.getStatus() == TermsStatus.ACTIVE) {
            throw new IllegalStateException("Cannot archive active terms version");
        }

        termsVersion.archive();
        termsVersionRepository.save(termsVersion);
    }
}
