package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository interface for UserTermsAcceptance domain entity
 */
public interface UserTermsAcceptanceRepository {

    /**
     * Save a user terms acceptance record
     */
    UserTermsAcceptance save(UserTermsAcceptance acceptance);

    /**
     * Find acceptance by ID
     */
    Optional<UserTermsAcceptance> findById(UUID id);

    /**
     * Find all acceptances by user ID
     */
    List<UserTermsAcceptance> findAllByUserId(UUID userId);

    /**
     * Find latest acceptance by user ID and terms type
     */
    Optional<UserTermsAcceptance> findLatestByUserIdAndTermsType(UUID userId, String termsType);

    /**
     * Find user's acceptance of a specific terms version
     */
    Optional<UserTermsAcceptance> findByUserIdAndTermsVersionId(UUID userId, UUID termsVersionId);

    /**
     * Find all users who accepted a specific terms version
     */
    List<UserTermsAcceptance> findAllByTermsVersionId(UUID termsVersionId);

    /**
     * Find acceptances by acceptance type
     */
    List<UserTermsAcceptance> findAllByAcceptanceType(AcceptanceType acceptanceType);

    /**
     * Find acceptances within date range
     */
    List<UserTermsAcceptance> findAllByAcceptedAtBetween(LocalDateTime startDate, LocalDateTime endDate);

    /**
     * Check if user has accepted a specific terms version
     */
    boolean hasUserAcceptedVersion(UUID userId, UUID termsVersionId);

    /**
     * Check if user has accepted any active terms
     */
    boolean hasUserAcceptedActiveTerms(UUID userId, String termsType);

    /**
     * Count acceptances for a specific terms version
     */
    long countByTermsVersionId(UUID termsVersionId);

    /**
     * Find users who need to accept new terms
     * (users who haven't accepted the latest version)
     */
    List<UUID> findUserIdsWithoutLatestAcceptance(UUID latestTermsVersionId);

    /**
     * Delete acceptance record (soft delete)
     */
    void delete(UUID id);

    /**
     * Find all active acceptances by user
     */
    List<UserTermsAcceptance> findAllActiveByUserId(UUID userId);
}
