package com.flowlite.identifyservice.infrastructure.persistence.entities;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "TermsVersion", indexes = {
    @Index(name = "idx_terms_version_number", columnList = "version_number"),
    @Index(name = "idx_terms_type", columnList = "type"),
    @Index(name = "idx_terms_status", columnList = "status"),
    @Index(name = "idx_terms_active", columnList = "active")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TermsVersionEntity {

    @Id
    @Column(name = "id", columnDefinition = "BINARY(16)")
    private UUID id;

    // Version identification
    @Column(name = "version_number", nullable = false, length = 50, unique = true)
    private String versionNumber;

    @Column(name = "type", nullable = false, length = 30)
    private String type; // TERMS_OF_SERVICE, PRIVACY_POLICY

    // Content
    @Column(name = "title", nullable = false, length = 200)
    private String title;

    @Column(name = "content_text", columnDefinition = "TEXT")
    private String contentText;

    @Column(name = "content_url", length = 500)
    private String contentUrl;

    @Column(name = "change_summary", columnDefinition = "TEXT")
    private String changeSummary;

    // Version control flags
    @Column(name = "is_major_change", nullable = false)
    private Boolean isMajorChange;

    @Column(name = "requires_reacceptance", nullable = false)
    private Boolean requiresReacceptance;

    // Status management
    @Column(name = "status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private TermsStatusEnum status;

    // Dates
    @Column(name = "effective_date")
    private LocalDateTime effectiveDate;

    @Column(name = "created_at", updatable = false, nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    @Column(name = "superseded_at")
    private LocalDateTime supersededAt;

    // Metadata
    @Column(name = "created_by", length = 100)
    private String createdBy;

    @Column(name = "previous_version_id", columnDefinition = "BINARY(16)")
    private UUID previousVersionId;

    @Column(name = "active", nullable = false)
    private Boolean active;

    @PrePersist
    protected void onCreate() {
        if (id == null) {
            id = UUID.randomUUID();
        }
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
        if (active == null) {
            active = true;
        }
        if (status == null) {
            status = TermsStatusEnum.DRAFT;
        }
        if (isMajorChange == null) {
            isMajorChange = false;
        }
        if (requiresReacceptance == null) {
            requiresReacceptance = false;
        }
    }

    /**
     * Enum for Terms Status in persistence layer
     */
    public enum TermsStatusEnum {
        DRAFT,
        ACTIVE,
        SUPERSEDED,
        ARCHIVED
    }
}
