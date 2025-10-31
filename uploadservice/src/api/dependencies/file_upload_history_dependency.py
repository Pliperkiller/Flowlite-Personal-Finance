"""
Dependency injection for FileUploadHistoryRepository.
Add this to repositories.py or import it in your dependencies/__init__.py
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...infrastructure.database import get_database
from ...infrastructure.repositories.mysql_file_upload_history_repository import (
    MySQLFileUploadHistoryRepository
)


async def get_file_upload_history_repository(
    db: AsyncSession = Depends(get_database),
) -> MySQLFileUploadHistoryRepository:
    """
    Dependency for getting the file upload history repository.

    Args:
        db: Database session

    Returns:
        MySQLFileUploadHistoryRepository: File upload history repository instance
    """
    return MySQLFileUploadHistoryRepository(db)


# INSTRUCTIONS TO INTEGRATE:
#
# Option 1: Add to existing repositories.py
# --------------------------------------------
# 1. Add import at the top:
#    from ...infrastructure.repositories.mysql_file_upload_history_repository import (
#        MySQLFileUploadHistoryRepository
#    )
#
# 2. Add this function to repositories.py:
#    async def get_file_upload_history_repository(
#        db: AsyncSession = Depends(get_database),
#    ) -> MySQLFileUploadHistoryRepository:
#        return MySQLFileUploadHistoryRepository(db)
#
# Option 2: Import this file in dependencies/__init__.py
# -------------------------------------------------------
# Add to dependencies/__init__.py:
#    from .file_upload_history_dependency import get_file_upload_history_repository
#
# Then export it in __all__
