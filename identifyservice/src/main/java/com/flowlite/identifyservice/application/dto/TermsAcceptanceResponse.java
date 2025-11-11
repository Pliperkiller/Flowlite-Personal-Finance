package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO for Terms Acceptance response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Information about user's terms acceptance")
public class TermsAcceptanceResponse {

    @Schema(description = "Unique identifier of the acceptance record", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID id;

    @Schema(description = "User ID who accepted", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID userId;

    @Schema(description = "Terms version ID that was accepted", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID termsVersionId;

    @Schema(description = "Version number accepted", example = "v1.0_2025-01-15")
    String versionNumber;

    @Schema(description = "Type of acceptance", example = "INITIAL_SIGNUP")
    String acceptanceType;

    @Schema(description = "When the terms were accepted")
    LocalDateTime acceptedAt;

    @Schema(description = "IP address from which acceptance was made (masked)", example = "192.168.***.***")
    String ipAddress;

    @Schema(description = "Method of acceptance", example = "WEB")
    String acceptanceMethod;

    @Schema(description = "Country from which acceptance was made", example = "Colombia")
    String acceptedFromCountry;

    @Schema(description = "Whether acceptance was verified")
    boolean verified;

    @Schema(description = "Whether this acceptance is still active")
    boolean active;
}
