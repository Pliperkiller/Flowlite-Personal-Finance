package com.flowlite.identifyservice.infrastructure.persistence.entities;

import lombok.*;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "UserTermsAcceptance", indexes = {
    @Index(name = "idx_user_terms_user_id", columnList = "user_id"),
    @Index(name = "idx_user_terms_version_id", columnList = "terms_version_id"),
    @Index(name = "idx_user_terms_accepted_at", columnList = "accepted_at"),
    @Index(name = "idx_user_terms_active", columnList = "active"),
    @Index(name = "idx_user_terms_user_version", columnList = "user_id, terms_version_id")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserTermsAcceptanceEntity {

    @Id
    @Column(name = "id", columnDefinition = "BINARY(16)")
    private UUID id;

    @Column(name = "user_id", columnDefinition = "BINARY(16)", nullable = false)
    private UUID userId;

    @Column(name = "terms_version_id", columnDefinition = "BINARY(16)", nullable = false)
    private UUID termsVersionId;

    // Acceptance details
    @Column(name = "accepted_at", nullable = false)
    private LocalDateTime acceptedAt;

    @Column(name = "acceptance_type", nullable = false, length = 30)
    @Enumerated(EnumType.STRING)
    private AcceptanceTypeEnum acceptanceType;

    // Audit information
    @Column(name = "ip_address", length = 45) // IPv6 compatible
    private String ipAddress;

    @Column(name = "user_agent", length = 500)
    private String userAgent;

    @Column(name = "acceptance_method", length = 30)
    private String acceptanceMethod;

    // Geographic information (optional)
    @Column(name = "accepted_from_country", length = 100)
    private String acceptedFromCountry;

    @Column(name = "accepted_from_city", length = 100)
    private String acceptedFromCity;

    // Verification
    @Column(name = "verified", nullable = false)
    private Boolean verified;

    @Column(name = "verified_at")
    private LocalDateTime verifiedAt;

    // Metadata
    @Column(name = "created_at", updatable = false, nullable = false)
    private LocalDateTime createdAt;

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
        if (acceptedAt == null) {
            acceptedAt = LocalDateTime.now();
        }
        if (active == null) {
            active = true;
        }
        if (verified == null) {
            verified = false;
        }
    }

    /**
     * Enum for Acceptance Type in persistence layer
     */
    public enum AcceptanceTypeEnum {
        INITIAL_SIGNUP,
        FORCED_UPDATE,
        OPTIONAL_UPDATE,
        REACTIVATION
    }
}
