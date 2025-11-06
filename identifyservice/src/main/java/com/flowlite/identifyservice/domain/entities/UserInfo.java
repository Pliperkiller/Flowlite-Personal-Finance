package com.flowlite.identifyservice.domain.entities;

import com.flowlite.identifyservice.domain.valueobjects.IdentificationType;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity that stores user's personal information
 * Maintains a one-to-one relationship with User
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(of = "id")
@ToString(exclude = {"createdAt", "updatedAt"})
public class UserInfo {
    
    UUID id;
    UUID userId; // Reference to associated User

    // Basic personal information
    String firstName;
    String middleName; // Optional
    String lastName;
    String secondLastName;
    String phone;
    String address;
    String city;
    String state;
    String country;
    LocalDate birthDate;

    // Identification information
    String identificationNumber;
    IdentificationType identificationType;

    // Additional information
    String gender;
    String maritalStatus;
    String occupation;

    // Metadata
    LocalDateTime createdAt;
    LocalDateTime updatedAt;
    boolean active;
    
    // Utility methods
    public String getFullName() {
        StringBuilder fullName = new StringBuilder();

        if (firstName != null && !firstName.trim().isEmpty()) {
            fullName.append(firstName.trim());
        }

        if (middleName != null && !middleName.trim().isEmpty()) {
            fullName.append(" ").append(middleName.trim());
        }

        if (lastName != null && !lastName.trim().isEmpty()) {
            fullName.append(" ").append(lastName.trim());
        }

        if (secondLastName != null && !secondLastName.trim().isEmpty()) {
            fullName.append(" ").append(secondLastName.trim());
        }

        return fullName.toString().trim();
    }

    public void updateInformation(String firstName, String middleName, String lastName,
                                 String secondLastName, String phone, String address,
                                 String city, String state) {
        this.firstName = firstName;
        this.middleName = middleName;
        this.lastName = lastName;
        this.secondLastName = secondLastName;
        this.phone = phone;
        this.address = address;
        this.city = city;
        this.state = state;
        this.updatedAt = LocalDateTime.now();
    }

    public void updateIdentification(String identificationNumber, IdentificationType identificationType) {
        this.identificationNumber = identificationNumber;
        this.identificationType = identificationType;
        this.updatedAt = LocalDateTime.now();
    }

    public void deactivate() {
        this.active = false;
        this.updatedAt = LocalDateTime.now();
    }

    public void activate() {
        this.active = true;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean hasCompleteInformation() {
        return firstName != null && !firstName.trim().isEmpty() &&
               lastName != null && !lastName.trim().isEmpty() &&
               phone != null && !phone.trim().isEmpty() &&
               identificationNumber != null && !identificationNumber.trim().isEmpty() &&
               identificationType != null;
    }
}
