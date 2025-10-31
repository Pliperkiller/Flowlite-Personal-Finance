"""
MySQL implementation of FileUploadHistoryRepositoryPort.
Handles persistence of file upload history records.
"""
from typing import Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...domain.ports.file_upload_history_repository_port import FileUploadHistoryRepositoryPort
from ...domain.entities.file_upload_history import FileUploadHistory
from ..database.file_upload_history_model import FileUploadHistoryModel


class MySQLFileUploadHistoryRepository(FileUploadHistoryRepositoryPort):
    """
    MySQL implementation of file upload history repository.
    Uses SQLAlchemy async sessions for database operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_by_hash(self, user_id: str, file_hash: str) -> Optional[FileUploadHistory]:
        """
        Find a file upload record by user ID and file hash.

        This method is used to detect duplicate file uploads.
        The composite index (id_user, file_hash) makes this query very efficient.

        Args:
            user_id: The user who uploaded the file (UUID as string)
            file_hash: SHA256 hash of the file content

        Returns:
            FileUploadHistory if found, None otherwise
        """
        query = select(FileUploadHistoryModel).where(
            FileUploadHistoryModel.id_user == user_id,
            FileUploadHistoryModel.file_hash == file_hash
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def save(self, file_upload: FileUploadHistory) -> FileUploadHistory:
        """
        Save a new file upload history record.

        Args:
            file_upload: The file upload history to save

        Returns:
            The saved file upload history
        """
        # Generate UUID if not provided
        id_file = file_upload.id_file if file_upload.id_file else str(uuid4())
        
        model = FileUploadHistoryModel(
            id_file=id_file,
            id_user=file_upload.id_user,
            file_hash=file_upload.file_hash,
            file_name=file_upload.file_name,
            bank_code=file_upload.bank_code,
            upload_date=file_upload.upload_date,
            id_batch=file_upload.id_batch,
            file_size=file_upload.file_size,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, id_file: str) -> Optional[FileUploadHistory]:
        """
        Get file upload history by ID.

        Args:
            id_file: The file upload history ID (UUID as string)

        Returns:
            FileUploadHistory if found, None otherwise
        """
        query = select(FileUploadHistoryModel).where(
            FileUploadHistoryModel.id_file == id_file
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    def _to_entity(self, model: FileUploadHistoryModel) -> FileUploadHistory:
        """
        Convert database model to domain entity.

        Args:
            model: SQLAlchemy model instance

        Returns:
            Domain entity
        """
        return FileUploadHistory(
            id_file=model.id_file,
            id_user=model.id_user,
            file_hash=model.file_hash,
            file_name=model.file_name,
            bank_code=model.bank_code,
            upload_date=model.upload_date,
            id_batch=model.id_batch,
            file_size=model.file_size,
        )
