package com.flowlite.identifyservice.application.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO for creating a new terms version (Admin only)
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Schema(description = "Request to create a new terms version")
public class CreateTermsVersionRequest {

    @NotBlank(message = "Version number is required")
    @Size(min = 3, max = 50, message = "Version number must be between 3 and 50 characters")
    @Schema(description = "Version number", example = "v1.0_2025-01-15", required = true)
    String versionNumber;

    @NotBlank(message = "Type is required")
    @Schema(description = "Type of terms", example = "TERMS_OF_SERVICE", required = true)
    String type;

    @NotBlank(message = "Title is required")
    @Size(min = 5, max = 200, message = "Title must be between 5 and 200 characters")
    @Schema(description = "Title of the terms", example = "Flowlite Terms of Service", required = true)
    String title;

    @Schema(description = "Full text content")
    String contentText;

    @Schema(description = "URL to external document", example = "https://flowlite.com/terms/v1.0")
    String contentUrl;

    @Schema(description = "Summary of changes from previous version")
    String changeSummary;

    @NotNull(message = "Is major change flag is required")
    @Schema(description = "Whether this is a major change", example = "true", required = true)
    Boolean isMajorChange;

    @NotNull(message = "Requires reacceptance flag is required")
    @Schema(description = "Whether re-acceptance is required", example = "true", required = true)
    Boolean requiresReacceptance;

    @Schema(description = "When this version becomes effective")
    LocalDateTime effectiveDate;

    @Schema(description = "Previous version ID (for history tracking)", example = "550e8400-e29b-41d4-a716-446655440000")
    UUID previousVersionId;

    @Schema(description = "Created by (admin username/ID)", example = "admin")
    String createdBy;
}
