"""
SQLAlchemy model for FileUploadHistory table.
This file contains the database model that should be added to the infrastructure service.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from .models import Base, generate_uuid


class FileUploadHistoryModel(Base):
    """
    Database model for file upload history.
    Tracks uploaded files to prevent duplicate processing.

    Table Structure:
        - id_file: Primary key (UUID as string)
        - id_user: User who uploaded the file (references User from IdentityService)
        - file_hash: SHA256 hash of file content (64 hex characters)
        - file_name: Original filename
        - bank_code: Bank code (e.g., BANCOLOMBIA)
        - upload_date: Timestamp of upload
        - id_batch: Reference to TransactionBatch created from this file
        - file_size: Size of file in bytes

    Indexes:
        - idx_user_hash: Composite index on (id_user, file_hash) for fast duplicate detection
        - Individual indexes on id_user and file_hash for flexible querying
    """
    __tablename__ = "FileUploadHistory"

    id_file = Column(CHAR(36), primary_key=True, default=generate_uuid)
    # id_user references User table managed by IdentityService - no FK constraint
    id_user = Column(CHAR(36), nullable=False, index=True)
    file_hash = Column(CHAR(64), nullable=False, index=True)  # SHA256 = 64 hex chars
    file_name = Column(String(255), nullable=False)
    bank_code = Column(String(50), nullable=False)
    upload_date = Column(DateTime, nullable=False, default=func.now())
    id_batch = Column(CHAR(36), ForeignKey("TransactionBatch.id_batch"), nullable=False)
    file_size = Column(Integer, nullable=False)

    # Composite index for fast duplicate detection
    __table_args__ = (
        Index('idx_user_hash', 'id_user', 'file_hash'),
    )
