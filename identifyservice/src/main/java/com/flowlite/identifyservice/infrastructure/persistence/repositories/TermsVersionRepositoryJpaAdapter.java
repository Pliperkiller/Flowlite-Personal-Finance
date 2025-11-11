package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.domain.entities.TermsVersion;
import com.flowlite.identifyservice.domain.repositories.TermsVersionRepository;
import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;
import com.flowlite.identifyservice.infrastructure.persistence.entities.TermsVersionEntity;
import com.flowlite.identifyservice.infrastructure.persistence.mappers.TermsVersionMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class TermsVersionRepositoryJpaAdapter implements TermsVersionRepository {

    private final JpaTermsVersionRepository jpaTermsVersionRepository;

    @Override
    public TermsVersion save(TermsVersion termsVersion) {
        var entity = TermsVersionMapper.toEntity(termsVersion);
        var saved = jpaTermsVersionRepository.save(entity);
        return TermsVersionMapper.toDomain(saved);
    }

    @Override
    public Optional<TermsVersion> findById(UUID id) {
        return jpaTermsVersionRepository.findById(id)
                .map(TermsVersionMapper::toDomain);
    }

    @Override
    public Optional<TermsVersion> findByVersionNumber(String versionNumber) {
        return jpaTermsVersionRepository.findByVersionNumber(versionNumber)
                .map(TermsVersionMapper::toDomain);
    }

    @Override
    public Optional<TermsVersion> findActiveByType(String type) {
        return jpaTermsVersionRepository.findActiveByType(type)
                .map(TermsVersionMapper::toDomain);
    }

    @Override
    public List<TermsVersion> findAllByType(String type) {
        return jpaTermsVersionRepository.findAllByType(type)
                .stream()
                .map(TermsVersionMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<TermsVersion> findAllByStatus(TermsStatus status) {
        var entityStatus = mapToEntityStatus(status);
        return jpaTermsVersionRepository.findAllByStatus(entityStatus)
                .stream()
                .map(TermsVersionMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<TermsVersion> findAllActive() {
        return jpaTermsVersionRepository.findAllActive()
                .stream()
                .map(TermsVersionMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public List<TermsVersion> findHistoryByType(String type) {
        return jpaTermsVersionRepository.findHistoryByType(type)
                .stream()
                .map(TermsVersionMapper::toDomain)
                .collect(Collectors.toList());
    }

    @Override
    public boolean existsByVersionNumber(String versionNumber) {
        return jpaTermsVersionRepository.existsByVersionNumber(versionNumber);
    }

    @Override
    public void delete(UUID id) {
        jpaTermsVersionRepository.findById(id).ifPresent(entity -> {
            entity.setActive(false);
            jpaTermsVersionRepository.save(entity);
        });
    }

    @Override
    public List<TermsVersion> findAllRequiringReacceptance() {
        return jpaTermsVersionRepository.findAllRequiringReacceptance()
                .stream()
                .map(TermsVersionMapper::toDomain)
                .collect(Collectors.toList());
    }

    private TermsVersionEntity.TermsStatusEnum mapToEntityStatus(TermsStatus status) {
        return switch (status) {
            case DRAFT -> TermsVersionEntity.TermsStatusEnum.DRAFT;
            case ACTIVE -> TermsVersionEntity.TermsStatusEnum.ACTIVE;
            case SUPERSEDED -> TermsVersionEntity.TermsStatusEnum.SUPERSEDED;
            case ARCHIVED -> TermsVersionEntity.TermsStatusEnum.ARCHIVED;
        };
    }
}
