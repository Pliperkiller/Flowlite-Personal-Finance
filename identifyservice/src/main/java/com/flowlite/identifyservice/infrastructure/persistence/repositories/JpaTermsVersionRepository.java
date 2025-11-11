package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.infrastructure.persistence.entities.TermsVersionEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface JpaTermsVersionRepository extends JpaRepository<TermsVersionEntity, UUID> {

    Optional<TermsVersionEntity> findByVersionNumber(String versionNumber);

    @Query("SELECT t FROM TermsVersionEntity t WHERE t.type = :type AND t.status = 'ACTIVE' AND t.active = true ORDER BY t.effectiveDate DESC")
    Optional<TermsVersionEntity> findActiveByType(@Param("type") String type);

    List<TermsVersionEntity> findAllByType(String type);

    List<TermsVersionEntity> findAllByStatus(TermsVersionEntity.TermsStatusEnum status);

    @Query("SELECT t FROM TermsVersionEntity t WHERE t.active = true ORDER BY t.createdAt DESC")
    List<TermsVersionEntity> findAllActive();

    @Query("SELECT t FROM TermsVersionEntity t WHERE t.type = :type ORDER BY t.createdAt DESC")
    List<TermsVersionEntity> findHistoryByType(@Param("type") String type);

    boolean existsByVersionNumber(String versionNumber);

    @Query("SELECT t FROM TermsVersionEntity t WHERE t.requiresReacceptance = true AND t.status = 'ACTIVE'")
    List<TermsVersionEntity> findAllRequiringReacceptance();
}
