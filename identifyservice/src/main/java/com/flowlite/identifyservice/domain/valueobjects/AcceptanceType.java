package com.flowlite.identifyservice.domain.valueobjects;

/**
 * Type of terms acceptance by user
 */
public enum AcceptanceType {
    /**
     * Initial acceptance during signup
     */
    INITIAL_SIGNUP,

    /**
     * Forced update due to major changes
     */
    FORCED_UPDATE,

    /**
     * Optional update (user chose to review and accept)
     */
    OPTIONAL_UPDATE,

    /**
     * Re-acceptance after account recovery
     */
    REACTIVATION
}
