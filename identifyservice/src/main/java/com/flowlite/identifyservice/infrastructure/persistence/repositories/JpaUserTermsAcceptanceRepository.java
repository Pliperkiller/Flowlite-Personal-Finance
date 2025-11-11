package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.infrastructure.persistence.entities.UserTermsAcceptanceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface JpaUserTermsAcceptanceRepository extends JpaRepository<UserTermsAcceptanceEntity, UUID> {

    List<UserTermsAcceptanceEntity> findAllByUserId(UUID userId);

    @Query("SELECT a FROM UserTermsAcceptanceEntity a " +
           "JOIN TermsVersionEntity t ON a.termsVersionId = t.id " +
           "WHERE a.userId = :userId AND t.type = :termsType AND a.active = true " +
           "ORDER BY a.acceptedAt DESC")
    Optional<UserTermsAcceptanceEntity> findLatestByUserIdAndTermsType(
            @Param("userId") UUID userId,
            @Param("termsType") String termsType);

    Optional<UserTermsAcceptanceEntity> findByUserIdAndTermsVersionId(UUID userId, UUID termsVersionId);

    List<UserTermsAcceptanceEntity> findAllByTermsVersionId(UUID termsVersionId);

    List<UserTermsAcceptanceEntity> findAllByAcceptanceType(UserTermsAcceptanceEntity.AcceptanceTypeEnum acceptanceType);

    List<UserTermsAcceptanceEntity> findAllByAcceptedAtBetween(LocalDateTime startDate, LocalDateTime endDate);

    @Query("SELECT CASE WHEN COUNT(a) > 0 THEN true ELSE false END " +
           "FROM UserTermsAcceptanceEntity a " +
           "WHERE a.userId = :userId AND a.termsVersionId = :termsVersionId AND a.active = true")
    boolean existsByUserIdAndTermsVersionId(@Param("userId") UUID userId, @Param("termsVersionId") UUID termsVersionId);

    @Query("SELECT CASE WHEN COUNT(a) > 0 THEN true ELSE false END " +
           "FROM UserTermsAcceptanceEntity a " +
           "JOIN TermsVersionEntity t ON a.termsVersionId = t.id " +
           "WHERE a.userId = :userId AND t.type = :termsType AND t.status = 'ACTIVE' AND a.active = true")
    boolean existsActiveAcceptanceByUserIdAndType(@Param("userId") UUID userId, @Param("termsType") String termsType);

    long countByTermsVersionId(UUID termsVersionId);

    // Note: This query would require access to UserEntity which may not be in same context
    // For now, this functionality should be implemented at the service layer
    // by querying all users and filtering
    @Query("SELECT DISTINCT a.userId FROM UserTermsAcceptanceEntity a " +
           "WHERE a.termsVersionId != :latestTermsVersionId OR " +
           "a.userId NOT IN (SELECT a2.userId FROM UserTermsAcceptanceEntity a2 WHERE a2.termsVersionId = :latestTermsVersionId)")
    List<UUID> findUserIdsWithoutLatestAcceptance(@Param("latestTermsVersionId") UUID latestTermsVersionId);

    @Query("SELECT a FROM UserTermsAcceptanceEntity a WHERE a.userId = :userId AND a.active = true ORDER BY a.acceptedAt DESC")
    List<UserTermsAcceptanceEntity> findAllActiveByUserId(@Param("userId") UUID userId);
}
