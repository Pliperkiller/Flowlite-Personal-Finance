package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for TermsVersion domain entity
 */
public interface TermsVersionRepository {

    /**
     * Save a terms version
     */
    TermsVersion save(TermsVersion termsVersion);

    /**
     * Find terms version by ID
     */
    Optional<TermsVersion> findById(UUID id);

    /**
     * Find terms version by version number
     */
    Optional<TermsVersion> findByVersionNumber(String versionNumber);

    /**
     * Find current active terms version by type
     */
    Optional<TermsVersion> findActiveByType(String type);

    /**
     * Find all terms versions by type
     */
    List<TermsVersion> findAllByType(String type);

    /**
     * Find all terms versions by status
     */
    List<TermsVersion> findAllByStatus(TermsStatus status);

    /**
     * Find all active terms versions
     */
    List<TermsVersion> findAllActive();

    /**
     * Find terms version history by type (ordered by creation date)
     */
    List<TermsVersion> findHistoryByType(String type);

    /**
     * Check if a version number already exists
     */
    boolean existsByVersionNumber(String versionNumber);

    /**
     * Delete terms version (soft delete by marking inactive)
     */
    void delete(UUID id);

    /**
     * Find all versions that require re-acceptance
     */
    List<TermsVersion> findAllRequiringReacceptance();
}
