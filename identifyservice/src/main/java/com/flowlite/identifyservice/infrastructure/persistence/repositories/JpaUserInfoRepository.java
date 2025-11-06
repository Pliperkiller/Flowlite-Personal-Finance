package com.flowlite.identifyservice.infrastructure.persistence.repositories;

import com.flowlite.identifyservice.infrastructure.persistence.entities.UserInfoEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface JpaUserInfoRepository extends JpaRepository<UserInfoEntity, UUID> {

    Optional<UserInfoEntity> findByUserId(UUID userId);

    Optional<UserInfoEntity> findByIdentificationNumber(String identificationNumber);

    Optional<UserInfoEntity> findByPhone(String phone);

    List<UserInfoEntity> findByFirstNameAndMiddleNameAndLastNameAndSecondLastName(
        String firstName, String middleName, String lastName, String secondLastName);

    List<UserInfoEntity> findByFirstName(String firstName);

    List<UserInfoEntity> findByLastName(String lastName);

    List<UserInfoEntity> findByCity(String city);

    List<UserInfoEntity> findByState(String state);

    @Query("SELECT u FROM UserInfoEntity u WHERE u.firstName IS NOT NULL AND u.firstName != '' " +
           "AND u.lastName IS NOT NULL AND u.lastName != '' " +
           "AND u.phone IS NOT NULL AND u.phone != '' " +
           "AND u.identificationNumber IS NOT NULL AND u.identificationNumber != ''")
    List<UserInfoEntity> findUsersWithCompleteInfo();

    boolean existsByUserId(UUID userId);

    boolean existsByIdentificationNumber(String identificationNumber);

    boolean existsByPhone(String phone);
}
