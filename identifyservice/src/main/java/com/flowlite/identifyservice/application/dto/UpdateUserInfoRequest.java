package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

/**
 * DTO for updating user's personal information
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Request to update user's personal information")
public class UpdateUserInfoRequest {

    @NotBlank(message = "First name is required")
    @Size(min = 2, max = 50, message = "First name must be between 2 and 50 characters")
    @Schema(description = "User's first name", example = "John", required = true)
    String firstName;

    @Size(max = 50, message = "Middle name cannot exceed 50 characters")
    @Schema(description = "User's middle name (optional)", example = "Michael")
    String middleName;

    @NotBlank(message = "Last name is required")
    @Size(min = 2, max = 50, message = "Last name must be between 2 and 50 characters")
    @Schema(description = "User's last name", example = "Smith", required = true)
    String lastName;

    @Size(max = 50, message = "Second last name cannot exceed 50 characters")
    @Schema(description = "User's second last name (optional)", example = "Johnson")
    String secondLastName;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[0-9]{10,15}$", message = "Phone number must contain only digits and be between 10 and 15 characters")
    @Schema(description = "User's phone number", example = "3001234567", required = true)
    String phone;

    @Size(max = 200, message = "Address cannot exceed 200 characters")
    @Schema(description = "User's address", example = "123 Main St #45-67")
    String address;

    @Size(max = 100, message = "City cannot exceed 100 characters")
    @Schema(description = "User's city", example = "New York")
    String city;

    @Size(max = 100, message = "State cannot exceed 100 characters")
    @Schema(description = "User's state/province", example = "New York")
    String state;

    @Size(max = 100, message = "Country cannot exceed 100 characters")
    @Schema(description = "User's country", example = "USA")
    String country;

    @Schema(description = "User's birth date", example = "1990-05-15")
    LocalDate birthDate;

    @NotBlank(message = "Identification number is required")
    @Pattern(regexp = "^[0-9]{6,20}$", message = "Identification number must contain only digits and be between 6 and 20 characters")
    @Schema(description = "User's identification number", example = "12345678", required = true)
    String identificationNumber;

    @NotNull(message = "Identification type is required")
    @Schema(description = "User's identification type", example = "CC", required = true)
    String identificationType;

    @Size(max = 20, message = "Gender cannot exceed 20 characters")
    @Schema(description = "User's gender", example = "Male")
    String gender;

    @Size(max = 30, message = "Marital status cannot exceed 30 characters")
    @Schema(description = "User's marital status", example = "Single")
    String maritalStatus;

    @Size(max = 100, message = "Occupation cannot exceed 100 characters")
    @Schema(description = "User's occupation", example = "Engineer")
    String occupation;
}
