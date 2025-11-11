package com.flowlite.identifyservice.application.services;

import com.flowlite.identifyservice.domain.entities.UserInfo;
import com.flowlite.identifyservice.domain.repositories.UserInfoRepository;
import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import lombok.*;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Service for managing complete user information
 */
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@Slf4j
public class CompleteInfoUserService {

    UserInfoRepository userInfoRepository;

    /**
     * Creates or updates a user's personal information
     */
    @Transactional
    public UserInfo saveUserInfo(@NonNull UUID userId, @NonNull String firstName, String middleName,
                               @NonNull String lastName, String secondLastName, @NonNull String phone,
                               String address, String city, String state, String country,
                               LocalDate birthDate, @NonNull String identificationNumber,
                               @NonNull IdentificationType identificationType, String gender,
                               String maritalStatus, String occupation) {

        // Check if information already exists for this user
        Optional<UserInfo> existingInfo = userInfoRepository.findByUserId(userId);

        UserInfo userInfo;
        if (existingInfo.isPresent()) {
            // Update existing information
            userInfo = existingInfo.get();
            userInfo.updateInformation(firstName, middleName, lastName,
                                     secondLastName, phone, address, city, state);
            userInfo.updateIdentification(identificationNumber, identificationType);

            // Update additional fields
            userInfo.setGender(gender);
            userInfo.setMaritalStatus(maritalStatus);
            userInfo.setOccupation(occupation);
            userInfo.setCountry(country);
            userInfo.setBirthDate(birthDate);
        } else {
            // Create new information
            userInfo = UserInfo.builder()
                    .id(UUID.randomUUID())
                    .userId(userId)
                    .firstName(firstName)
                    .middleName(middleName)
                    .lastName(lastName)
                    .secondLastName(secondLastName)
                    .phone(phone)
                    .address(address)
                    .city(city)
                    .state(state)
                    .country(country)
                    .birthDate(birthDate)
                    .identificationNumber(identificationNumber)
                    .identificationType(identificationType)
                    .gender(gender)
                    .maritalStatus(maritalStatus)
                    .occupation(occupation)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .active(true)
                    .build();
        }

        return userInfoRepository.save(userInfo);
    }

    /**
     * Gets a user's personal information
     */
    public Optional<UserInfo> getUserInfo(@NonNull UUID userId) {
        return userInfoRepository.findByUserId(userId);
    }

    /**
     * Gets personal information by ID
     */
    public Optional<UserInfo> getUserInfoById(@NonNull UUID userInfoId) {
        return userInfoRepository.findById(userInfoId);
    }

    /**
     * Searches users by full name
     */
    public List<UserInfo> searchByFullName(@NonNull String firstName, String middleName,
                                          @NonNull String lastName, String secondLastName) {
        return userInfoRepository.findByFullName(firstName, middleName,
                                                lastName, secondLastName);
    }

    /**
     * Searches users by first name
     */
    public List<UserInfo> searchByFirstName(@NonNull String firstName) {
        return userInfoRepository.findByFirstName(firstName);
    }

    /**
     * Searches users by last name
     */
    public List<UserInfo> searchByLastName(@NonNull String lastName) {
        return userInfoRepository.findByLastName(lastName);
    }

    /**
     * Searches users by city
     */
    public List<UserInfo> searchByCity(@NonNull String city) {
        return userInfoRepository.findByCity(city);
    }

    /**
     * Searches users by state
     */
    public List<UserInfo> searchByState(@NonNull String state) {
        return userInfoRepository.findByState(state);
    }

    /**
     * Gets all users with complete information
     */
    public List<UserInfo> getUsersWithCompleteInfo() {
        return userInfoRepository.findUsersWithCompleteInfo();
    }

    /**
     * Gets all active users
     */
    public List<UserInfo> getActiveUsers() {
        return userInfoRepository.findActiveUsers();
    }

    /**
     * Checks if a user has personal information
     */
    public boolean hasUserInfo(@NonNull UUID userId) {
        return userInfoRepository.existsByUserId(userId);
    }

    /**
     * Checks if an identification number is already in use
     */
    public boolean isIdentificationInUse(@NonNull String identificationNumber) {
        return userInfoRepository.existsByIdentificationNumber(identificationNumber);
    }

    /**
     * Checks if a phone number is already in use
     */
    public boolean isPhoneInUse(@NonNull String phone) {
        return userInfoRepository.existsByPhone(phone);
    }

    /**
     * Deactivates a user's personal information
     */
    @Transactional
    public void deactivateUserInfo(@NonNull UUID userId) {
        userInfoRepository.findByUserId(userId)
                .ifPresent(userInfo -> {
                    userInfo.deactivate();
                    userInfoRepository.save(userInfo);
                });
    }

    /**
     * Activates a user's personal information
     */
    @Transactional
    public void activateUserInfo(@NonNull UUID userId) {
        userInfoRepository.findByUserId(userId)
                .ifPresent(userInfo -> {
                    userInfo.activate();
                    userInfoRepository.save(userInfo);
                });
    }

    /**
     * Deletes a user's personal information
     */
    @Transactional
    public void deleteUserInfo(@NonNull UUID userId) {
        userInfoRepository.deleteByUserId(userId);
    }

    /**
     * Deletes personal information by ID
     */
    @Transactional
    public void deleteUserInfoById(@NonNull UUID userInfoId) {
        userInfoRepository.deleteById(userInfoId);
    }

    /**
     * Validates if personal information is complete
     */
    public boolean isUserInfoComplete(@NonNull UUID userId) {
        return userInfoRepository.findByUserId(userId)
                .map(UserInfo::hasCompleteInformation)
                .orElse(false);
    }
}
