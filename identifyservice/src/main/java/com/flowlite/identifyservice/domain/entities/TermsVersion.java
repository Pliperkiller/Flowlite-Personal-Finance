package com.flowlite.identifyservice.domain.entities;

import com.flowlite.identifyservice.domain.valueobjects.TermsStatus;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity that represents a version of Terms and Conditions or Privacy Policy
 * Maintains versioning history and tracks what changes were made
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(of = "id")
@ToString(exclude = {"contentText"})
public class TermsVersion {

    UUID id;

    // Version identification
    String versionNumber; // e.g., "v1.0_2025-01-15", "v2.0_2025-06-20"
    String type; // "TERMS_OF_SERVICE" or "PRIVACY_POLICY"

    // Content
    String title;
    String contentText; // Full text of terms (can be large)
    String contentUrl; // Alternative: URL to external document
    String changeSummary; // Summary of what changed from previous version

    // Version control flags
    boolean isMajorChange; // If true, requires user re-acceptance
    boolean requiresReacceptance; // Explicitly mark if re-acceptance is needed

    // Status management
    TermsStatus status; // DRAFT, ACTIVE, SUPERSEDED, ARCHIVED

    // Dates
    LocalDateTime effectiveDate; // When this version becomes effective
    LocalDateTime createdAt;
    LocalDateTime publishedAt; // When it was published
    LocalDateTime supersededAt; // When it was replaced by newer version

    // Metadata
    String createdBy; // User/admin who created this version
    UUID previousVersionId; // Reference to previous version for history

    boolean active;

    /**
     * Activates this version and marks it as published
     */
    public void activate() {
        this.status = TermsStatus.ACTIVE;
        this.publishedAt = LocalDateTime.now();
        this.active = true;
    }

    /**
     * Marks this version as superseded by a newer version
     */
    public void supersede() {
        this.status = TermsStatus.SUPERSEDED;
        this.supersededAt = LocalDateTime.now();
        this.active = false;
    }

    /**
     * Archives this version (soft delete)
     */
    public void archive() {
        this.status = TermsStatus.ARCHIVED;
        this.active = false;
    }

    /**
     * Checks if this version is currently active and effective
     */
    public boolean isCurrentlyActive() {
        return this.status == TermsStatus.ACTIVE
            && this.active
            && (this.effectiveDate == null || this.effectiveDate.isBefore(LocalDateTime.now()));
    }

    /**
     * Checks if users need to accept this version
     */
    public boolean needsUserAcceptance() {
        return this.requiresReacceptance || this.isMajorChange;
    }

    /**
     * Gets a formatted display version
     */
    public String getDisplayVersion() {
        return String.format("%s - %s", versionNumber, type);
    }
}
