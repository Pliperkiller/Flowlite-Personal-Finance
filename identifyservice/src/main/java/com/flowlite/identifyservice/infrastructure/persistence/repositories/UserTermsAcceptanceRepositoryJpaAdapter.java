package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.domain.entities.UserTermsAcceptance;
import com.flowlite.identifyservice.domain.repositories.UserTermsAcceptanceRepository;
import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;
import com.flowlite.identifyservice.infrastructure.persistence.entities.UserTermsAcceptanceEntity;
import com.flowlite.identifyservice.infrastructure.persistence.mappers.UserTermsAcceptanceMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class UserTermsAcceptanceRepositoryJpaAdapter implements UserTermsAcceptanceRepository {

    private final JpaUserTermsAcceptanceRepository jpaUserTermsAcceptanceRepository;

    @Override
    public UserTermsAcceptance save(UserTermsAcceptance acceptance) {
        var entity = UserTermsAcceptanceMapper.toEntity(acceptance);
        var saved = jpaUserTermsAcceptanceRepository.save(entity);
        return UserTermsAcceptanceMapper.toDomain(saved);
    }

    @Override
    public Optional<UserTermsAcceptance> findById(UUID id) {
        return jpaUserTermsAcceptanceRepository.findById(id)
                .map(UserTermsAcceptanceMapper::toDomain);
    }

    @Override
    public List<UserTermsAcceptance> findAllByUserId(UUID userId) {
        return jpaUserTermsAcceptanceRepository.findAllByUserId(userId)
                .stream()
                .map(UserTermsAcceptanceMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public Optional<UserTermsAcceptance> findLatestByUserIdAndTermsType(UUID userId, String termsType) {
        return jpaUserTermsAcceptanceRepository.findLatestByUserIdAndTermsType(userId, termsType)
                .map(UserTermsAcceptanceMapper::toDomain);
    }

    @Override
    public Optional<UserTermsAcceptance> findByUserIdAndTermsVersionId(UUID userId, UUID termsVersionId) {
        return jpaUserTermsAcceptanceRepository.findByUserIdAndTermsVersionId(userId, termsVersionId)
                .map(UserTermsAcceptanceMapper::toDomain);
    }

    @Override
    public List<UserTermsAcceptance> findAllByTermsVersionId(UUID termsVersionId) {
        return jpaUserTermsAcceptanceRepository.findAllByTermsVersionId(termsVersionId)
                .stream()
                .map(UserTermsAcceptanceMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserTermsAcceptance> findAllByAcceptanceType(AcceptanceType acceptanceType) {
        var entityType = mapToEntityType(acceptanceType);
        return jpaUserTermsAcceptanceRepository.findAllByAcceptanceType(entityType)
                .stream()
                .map(UserTermsAcceptanceMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserTermsAcceptance> findAllByAcceptedAtBetween(LocalDateTime startDate, LocalDateTime endDate) {
        return jpaUserTermsAcceptanceRepository.findAllByAcceptedAtBetween(startDate, endDate)
                .stream()
                .map(UserTermsAcceptanceMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public boolean hasUserAcceptedVersion(UUID userId, UUID termsVersionId) {
        return jpaUserTermsAcceptanceRepository.existsByUserIdAndTermsVersionId(userId, termsVersionId);
    }

    @Override
    public boolean hasUserAcceptedActiveTerms(UUID userId, String termsType) {
        return jpaUserTermsAcceptanceRepository.existsActiveAcceptanceByUserIdAndType(userId, termsType);
    }

    @Override
    public long countByTermsVersionId(UUID termsVersionId) {
        return jpaUserTermsAcceptanceRepository.countByTermsVersionId(termsVersionId);
    }

    @Override
    public List<UUID> findUserIdsWithoutLatestAcceptance(UUID latestTermsVersionId) {
        return jpaUserTermsAcceptanceRepository.findUserIdsWithoutLatestAcceptance(latestTermsVersionId);
    }

    @Override
    public void delete(UUID id) {
        jpaUserTermsAcceptanceRepository.findById(id).ifPresent(entity -> {
            entity.setActive(false);
            jpaUserTermsAcceptanceRepository.save(entity);
        });
    }

    @Override
    public List<UserTermsAcceptance> findAllActiveByUserId(UUID userId) {
        return jpaUserTermsAcceptanceRepository.findAllActiveByUserId(userId)
                .stream()
                .map(UserTermsAcceptanceMapper::toDomain)
                .collect(Collectors.toList());
    }

    private UserTermsAcceptanceEntity.AcceptanceTypeEnum mapToEntityType(AcceptanceType acceptanceType) {
        return switch (acceptanceType) {
            case INITIAL_SIGNUP -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.INITIAL_SIGNUP;
            case FORCED_UPDATE -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.FORCED_UPDATE;
            case OPTIONAL_UPDATE -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.OPTIONAL_UPDATE;
            case REACTIVATION -> UserTermsAcceptanceEntity.AcceptanceTypeEnum.REACTIVATION;
        };
    }
}
