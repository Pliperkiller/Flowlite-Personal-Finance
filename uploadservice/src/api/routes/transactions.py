from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Header
from typing import List
from pydantic import BaseModel
from uuid import UUID
from ...application.use_cases import ProcessFilesUseCase, GetBatchStatusUseCase
from ...application.dto import BatchStatusDTO
from ..dependencies import (
    get_current_user_id,
    get_transaction_repository,
    get_bank_repository,
    get_category_repository,
    get_batch_repository,
    get_classifier,
    get_message_broker,
    get_db_session_factory,
)
from ...infrastructure.parsers import ParserFactory

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


class UploadResponse(BaseModel):
    batch_id: UUID
    message: str


from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_files(
    bank_code: str,
    files: List[UploadFile] = File(...),
    authorization: HTTPAuthorizationCredentials = Security(security),
    user_id: UUID = Depends(get_current_user_id),
    transaction_repo=Depends(get_transaction_repository),
    bank_repo=Depends(get_bank_repository),
    category_repo=Depends(get_category_repository),
    batch_repo=Depends(get_batch_repository),
    classifier=Depends(get_classifier),
    message_broker=Depends(get_message_broker),
    session_factory=Depends(get_db_session_factory),
):
    """
    Endpoint for uploading Excel files with transactions.

    Args:
        bank_code: Bank code (e.g., BANCOLOMBIA)
        files: List of Excel files to process
        user_id: Current authenticated user ID
        transaction_repo: Transaction repository dependency
        bank_repo: Bank repository dependency
        category_repo: Category repository dependency
        batch_repo: Batch repository dependency
        classifier: Transaction classifier dependency
        session_factory: Database session factory dependency

    Returns:
        UploadResponse: Contains the batch ID for checking processing status

    Raises:
        HTTPException: If files are invalid or processing fails
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide at least one file",
        )

    # Validate that all files are Excel files
    for file in files:
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a valid Excel file",
            )

    try:
        # Get the appropriate parser
        parser = ParserFactory.get_parser(bank_code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Read file contents
    files_content = []
    for file in files:
        content = await file.read()
        files_content.append(content)

    # Create the use case and execute
    use_case = ProcessFilesUseCase(
        transaction_repo=transaction_repo,
        bank_repo=bank_repo,
        category_repo=category_repo,
        batch_repo=batch_repo,
        classifier=classifier,
        message_broker=message_broker,
        session_factory=session_factory,
    )

    try:
        batch_id = await use_case.execute(
            files_content=files_content,
            parser=parser,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return UploadResponse(
        batch_id=batch_id,
        message=f"Processing started. Use batch_id {batch_id} to check the status.",
    )


@router.get("/batch/{batch_id}", response_model=BatchStatusDTO)
async def get_batch_status(
    batch_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    batch_repo=Depends(get_batch_repository),
):
    """
    Query the processing status of a transaction batch.

    Args:
        batch_id: ID of the batch to query
        user_id: Current authenticated user ID
        batch_repo: Batch repository dependency

    Returns:
        BatchStatusDTO: Batch status with progress percentage

    Raises:
        HTTPException: If batch is not found or user lacks permissions
    """
    use_case = GetBatchStatusUseCase(batch_repo=batch_repo)
    batch_status = await use_case.execute(batch_id=batch_id)

    if not batch_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found",
        )

    return batch_status
