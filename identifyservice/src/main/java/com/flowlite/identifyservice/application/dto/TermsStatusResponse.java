package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO for user's terms status response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "User's current terms and conditions status")
public class TermsStatusResponse {

    @Schema(description = "User ID", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID userId;

    @Schema(description = "Current active terms version ID", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID currentTermsVersionId;

    @Schema(description = "Current active version number", example = "v1.0_2025-01-15")
    String currentVersionNumber;

    @Schema(description = "User's accepted terms version ID (may be null if not accepted)", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID acceptedTermsVersionId;

    @Schema(description = "User's accepted version number (may be null if not accepted)", example = "v1.0_2025-01-15")
    String acceptedVersionNumber;

    @Schema(description = "Whether user needs to accept new terms")
    boolean needsAcceptance;

    @Schema(description = "Whether the current version requires re-acceptance")
    boolean requiresReacceptance;

    @Schema(description = "Whether this is a major change")
    boolean isMajorChange;

    @Schema(description = "When user accepted their current version")
    LocalDateTime acceptedAt;

    @Schema(description = "Summary of changes in the new version (if needs acceptance)")
    String changeSummary;

    @Schema(description = "Message to display to user")
    String message;
}
