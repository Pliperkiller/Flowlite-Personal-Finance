package com.flowlite.identifyservice.domain.valueobjects;

/**
 * Status of a Terms Version in its lifecycle
 */
public enum TermsStatus {
    /**
     * Draft version, not yet published
     */
    DRAFT,

    /**
     * Currently active and in effect
     */
    ACTIVE,

    /**
     * Replaced by a newer version
     */
    SUPERSEDED,

    /**
     * Archived (soft deleted)
     */
    ARCHIVED
}
