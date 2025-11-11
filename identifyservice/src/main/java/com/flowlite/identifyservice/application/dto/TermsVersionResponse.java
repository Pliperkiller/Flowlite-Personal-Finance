package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO for Terms Version response
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Terms and Conditions version information")
public class TermsVersionResponse {

    @Schema(description = "Unique identifier of the terms version", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID id;

    @Schema(description = "Version number", example = "v1.0_2025-01-15")
    String versionNumber;

    @Schema(description = "Type of terms", example = "TERMS_OF_SERVICE")
    String type;

    @Schema(description = "Title of the terms", example = "Flowlite Terms of Service")
    String title;

    @Schema(description = "Full text content (may be large)")
    String contentText;

    @Schema(description = "URL to external document", example = "https://flowlite.com/terms/v1.0")
    String contentUrl;

    @Schema(description = "Summary of changes from previous version")
    String changeSummary;

    @Schema(description = "Whether this is a major change requiring user acceptance")
    boolean isMajorChange;

    @Schema(description = "Whether re-acceptance is required")
    boolean requiresReacceptance;

    @Schema(description = "Status of this version", example = "ACTIVE")
    String status;

    @Schema(description = "When this version becomes effective")
    LocalDateTime effectiveDate;

    @Schema(description = "When this version was created")
    LocalDateTime createdAt;

    @Schema(description = "When this version was published")
    LocalDateTime publishedAt;

    @Schema(description = "Whether this version is active")
    boolean active;
}
