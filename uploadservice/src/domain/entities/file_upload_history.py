"""
Domain entity for file upload history.
Used to track uploaded files and prevent duplicate processing.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FileUploadHistory:
    """
    Represents the history of a file upload.

    Attributes:
        id_file: Unique identifier for the file upload record (UUID as string)
        id_user: User who uploaded the file (UUID as string)
        file_hash: SHA256 hash of the file content (64 hex characters)
        file_name: Original name of the uploaded file
        bank_code: Bank code associated with the file (e.g., BANCOLOMBIA)
        upload_date: When the file was uploaded
        id_batch: Reference to the transaction batch created from this file (UUID as string)
        file_size: Size of the file in bytes
    """
    id_file: Optional[str]  # UUID as string, None before saving
    id_user: str  # UUID as string
    file_hash: str  # SHA256 hash (64 characters)
    file_name: str
    bank_code: str
    upload_date: datetime
    id_batch: str  # UUID as string
    file_size: int
