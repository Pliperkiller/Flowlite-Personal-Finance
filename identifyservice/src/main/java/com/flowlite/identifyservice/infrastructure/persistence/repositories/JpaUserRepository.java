package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import org.springframework.data.jpa.repository.JpaRepository;

import com.flowlite.identifyservice.infrastructure.persistence.entities.UserEntity;

import java.util.Optional;
import java.util.UUID;

public interface JpaUserRepository extends JpaRepository<UserEntity, UUID> {
    Optional<UserEntity> findByUsername(String username);
    Optional<UserEntity> findByEmail(String email);
}

