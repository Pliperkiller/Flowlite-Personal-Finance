"""
Repository port for FileUploadHistory.
Defines the interface for file upload history persistence.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.file_upload_history import FileUploadHistory


class FileUploadHistoryRepositoryPort(ABC):
    """
    Port interface for file upload history repository.
    Follows the port/adapter pattern from Clean Architecture.
    """

    @abstractmethod
    async def get_by_hash(self, user_id: str, file_hash: str) -> Optional[FileUploadHistory]:
        """
        Find a file upload record by user ID and file hash.

        Args:
            user_id: The user who uploaded the file (UUID as string)
            file_hash: SHA256 hash of the file content

        Returns:
            FileUploadHistory if found, None otherwise
        """
        pass

    @abstractmethod
    async def save(self, file_upload: FileUploadHistory) -> FileUploadHistory:
        """
        Save a new file upload history record.

        Args:
            file_upload: The file upload history to save

        Returns:
            The saved file upload history with generated ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, id_file: str) -> Optional[FileUploadHistory]:
        """
        Get file upload history by ID.

        Args:
            id_file: The file upload history ID (UUID as string)

        Returns:
            FileUploadHistory if found, None otherwise
        """
        pass
