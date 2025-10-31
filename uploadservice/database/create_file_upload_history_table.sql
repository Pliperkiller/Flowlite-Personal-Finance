-- ============================================================================
-- TABLE: FileUploadHistory
-- PURPOSE: Track uploaded files to prevent duplicate processing
-- CREATED: 2025-10-30
-- ============================================================================

-- Create FileUploadHistory table
CREATE TABLE IF NOT EXISTS FileUploadHistory (
    -- Primary Key
    id_file CHAR(36) NOT NULL PRIMARY KEY COMMENT 'Unique identifier for file upload record (UUID)',

    -- User reference (managed by IdentityService, no FK constraint)
    id_user CHAR(36) NOT NULL COMMENT 'User who uploaded the file (references User.id_user)',

    -- File identification
    file_hash CHAR(64) NOT NULL COMMENT 'SHA256 hash of file content (64 hex characters)',
    file_name VARCHAR(255) NOT NULL COMMENT 'Original filename',
    bank_code VARCHAR(50) NOT NULL COMMENT 'Bank code (e.g., BANCOLOMBIA)',
    file_size INT NOT NULL COMMENT 'File size in bytes',

    -- Timestamps
    upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When file was uploaded',

    -- Batch reference
    id_batch CHAR(36) NOT NULL COMMENT 'Transaction batch created from this file',

    -- Foreign Keys
    CONSTRAINT fk_file_upload_batch
        FOREIGN KEY (id_batch)
        REFERENCES TransactionBatch(id_batch)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Indexes for performance
    INDEX idx_user (id_user) COMMENT 'Index for querying by user',
    INDEX idx_hash (file_hash) COMMENT 'Index for hash lookups',
    INDEX idx_user_hash (id_user, file_hash) COMMENT 'Composite index for duplicate detection',
    INDEX idx_upload_date (upload_date) COMMENT 'Index for date range queries'

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Tracks uploaded files to prevent duplicate processing';


-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- Check if a file was already uploaded by a user
-- SELECT * FROM FileUploadHistory
-- WHERE id_user = 'user-uuid-here'
--   AND file_hash = 'sha256-hash-here';

-- Get upload history for a user
-- SELECT
--     file_name,
--     bank_code,
--     upload_date,
--     file_size,
--     id_batch
-- FROM FileUploadHistory
-- WHERE id_user = 'user-uuid-here'
-- ORDER BY upload_date DESC
-- LIMIT 10;

-- Find duplicate uploads (same hash, different users)
-- SELECT
--     file_hash,
--     COUNT(*) as upload_count,
--     GROUP_CONCAT(DISTINCT id_user) as users,
--     MIN(upload_date) as first_upload,
--     MAX(upload_date) as last_upload
-- FROM FileUploadHistory
-- GROUP BY file_hash
-- HAVING COUNT(*) > 1;


-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Get table statistics
-- SELECT
--     COUNT(*) as total_uploads,
--     COUNT(DISTINCT id_user) as unique_users,
--     COUNT(DISTINCT file_hash) as unique_files,
--     MIN(upload_date) as first_upload,
--     MAX(upload_date) as last_upload,
--     SUM(file_size) / 1024 / 1024 as total_mb
-- FROM FileUploadHistory;

-- Clean up old records (optional, run periodically)
-- Uncomment if you want to remove records older than 1 year
-- DELETE FROM FileUploadHistory
-- WHERE upload_date < DATE_SUB(NOW(), INTERVAL 1 YEAR);


-- ============================================================================
-- ROLLBACK (if needed)
-- ============================================================================
-- DROP TABLE IF EXISTS FileUploadHistory;
