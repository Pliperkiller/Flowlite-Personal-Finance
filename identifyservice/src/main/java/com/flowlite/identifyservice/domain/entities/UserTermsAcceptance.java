package com.flowlite.identifyservice.domain.entities;

import com.flowlite.identifyservice.domain.valueobjects.AcceptanceType;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity that records user acceptance of specific terms versions
 * Provides audit trail and legal compliance
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(of = "id")
@ToString
public class UserTermsAcceptance {

    UUID id;
    UUID userId; // Reference to User who accepted
    UUID termsVersionId; // Reference to TermsVersion that was accepted

    // Acceptance details
    LocalDateTime acceptedAt;
    AcceptanceType acceptanceType;

    // Audit information
    String ipAddress; // IP from which acceptance was made
    String userAgent; // Browser/device information
    String acceptanceMethod; // "WEB", "MOBILE_APP", "API"

    // Geographic information (optional)
    String acceptedFromCountry;
    String acceptedFromCity;

    // Verification
    boolean verified; // If acceptance was verified (e.g., email confirmation)
    LocalDateTime verifiedAt;

    // Metadata
    LocalDateTime createdAt;
    boolean active;

    /**
     * Creates a new acceptance record
     */
    public static UserTermsAcceptance createAcceptance(
            UUID userId,
            UUID termsVersionId,
            AcceptanceType acceptanceType,
            String ipAddress,
            String userAgent,
            String acceptanceMethod) {

        return UserTermsAcceptance.builder()
                .id(UUID.randomUUID())
                .userId(userId)
                .termsVersionId(termsVersionId)
                .acceptedAt(LocalDateTime.now())
                .acceptanceType(acceptanceType)
                .ipAddress(ipAddress)
                .userAgent(userAgent)
                .acceptanceMethod(acceptanceMethod)
                .verified(false)
                .createdAt(LocalDateTime.now())
                .active(true)
                .build();
    }

    /**
     * Marks this acceptance as verified
     */
    public void verify() {
        this.verified = true;
        this.verifiedAt = LocalDateTime.now();
    }

    /**
     * Deactivates this acceptance record
     */
    public void deactivate() {
        this.active = false;
    }

    /**
     * Checks if this acceptance is still valid
     */
    public boolean isValid() {
        return this.active && this.acceptedAt != null;
    }

    /**
     * Gets formatted acceptance information
     */
    public String getAcceptanceInfo() {
        return String.format("Accepted on %s via %s from IP %s",
                acceptedAt, acceptanceMethod, maskIpAddress(ipAddress));
    }

    /**
     * Masks IP address for privacy (shows only first two octets)
     */
    private String maskIpAddress(String ip) {
        if (ip == null || ip.isEmpty()) {
            return "N/A";
        }
        String[] parts = ip.split("\\.");
        if (parts.length == 4) {
            return parts[0] + "." + parts[1] + ".***.**";
        }
        return "***";
    }
}
