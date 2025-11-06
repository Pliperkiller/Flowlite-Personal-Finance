package com.flowlite.identifyservice.domain.repositories;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import lombok.NonNull;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for managing user's personal information
 */
public interface UserInfoRepository {

    /**
     * Finds user information by ID
     */
    Optional<UserInfo> findById(@NonNull UUID id);

    /**
     * Finds user information by associated user ID
     */
    Optional<UserInfo> findByUserId(@NonNull UUID userId);

    /**
     * Finds user information by identification number
     */
    Optional<UserInfo> findByIdentificationNumber(@NonNull String identificationNumber);

    /**
     * Finds user information by phone number
     */
    Optional<UserInfo> findByPhone(@NonNull String phone);

    /**
     * Finds user information by full name
     */
    List<UserInfo> findByFullName(@NonNull String firstName, String middleName,
                                  @NonNull String lastName, String secondLastName);

    /**
     * Finds user information by first name
     */
    List<UserInfo> findByFirstName(@NonNull String firstName);

    /**
     * Finds user information by last name
     */
    List<UserInfo> findByLastName(@NonNull String lastName);

    /**
     * Finds user information by city
     */
    List<UserInfo> findByCity(@NonNull String city);

    /**
     * Finds user information by state
     */
    List<UserInfo> findByState(@NonNull String state);

    /**
     * Finds all users with complete information
     */
    List<UserInfo> findUsersWithCompleteInfo();

    /**
     * Finds all active users
     */
    List<UserInfo> findActiveUsers();

    /**
     * Saves or updates user information
     */
    UserInfo save(@NonNull UserInfo userInfo);

    /**
     * Deletes user information by ID
     */
    void deleteById(@NonNull UUID id);

    /**
     * Deletes user information by user ID
     */
    void deleteByUserId(@NonNull UUID userId);

    /**
     * Checks if information exists for a user
     */
    boolean existsByUserId(@NonNull UUID userId);

    /**
     * Checks if information exists with an identification number
     */
    boolean existsByIdentificationNumber(@NonNull String identificationNumber);

    /**
     * Checks if information exists with a phone number
     */
    boolean existsByPhone(@NonNull String phone);
}
