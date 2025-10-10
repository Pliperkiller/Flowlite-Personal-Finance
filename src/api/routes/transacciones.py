from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from pydantic import BaseModel
from ...application.use_cases import ProcesarArchivosUseCase, ConsultarEstadoLoteUseCase
from ...application.dto import LoteStatusDTO
from ..dependencies import (
    get_current_user_id,
    get_transaccion_repository,
    get_banco_repository,
    get_categoria_repository,
    get_lote_repository,
    get_clasificador,
)
from ...infrastructure.parsers import ParserFactory

router = APIRouter(prefix="/api/v1/transacciones", tags=["transacciones"])


class UploadResponse(BaseModel):
    lote_id: int
    message: str


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_archivos(
    banco_codigo: str,
    archivos: List[UploadFile] = File(...),
    usuario_id: int = Depends(get_current_user_id),
    transaccion_repo=Depends(get_transaccion_repository),
    banco_repo=Depends(get_banco_repository),
    categoria_repo=Depends(get_categoria_repository),
    lote_repo=Depends(get_lote_repository),
    clasificador=Depends(get_clasificador),
):
    """
    Endpoint para cargar archivos de Excel con transacciones

    Args:
        banco_codigo: Código del banco (ej: BANCOLOMBIA)
        archivos: Lista de archivos Excel a procesar

    Returns:
        ID del lote creado para consultar el estado del procesamiento
    """
    if not archivos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos un archivo",
        )

    # Validar que todos los archivos sean Excel
    for archivo in archivos:
        if not archivo.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo {archivo.filename} no es un archivo Excel válido",
            )

    try:
        # Obtener el parser apropiado
        parser = ParserFactory.get_parser(banco_codigo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Leer contenido de los archivos
    archivos_content = []
    for archivo in archivos:
        content = await archivo.read()
        archivos_content.append(content)

    # Crear el caso de uso y ejecutar
    use_case = ProcesarArchivosUseCase(
        transaccion_repo=transaccion_repo,
        banco_repo=banco_repo,
        categoria_repo=categoria_repo,
        lote_repo=lote_repo,
        clasificador=clasificador,
    )

    try:
        lote_id = await use_case.execute(
            archivos_content=archivos_content,
            parser=parser,
            usuario_id=usuario_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return UploadResponse(
        lote_id=lote_id,
        message=f"Procesamiento iniciado. Use el lote_id {lote_id} para consultar el estado.",
    )


@router.get("/lote/{lote_id}", response_model=LoteStatusDTO)
async def get_lote_status(
    lote_id: int,
    usuario_id: int = Depends(get_current_user_id),
    lote_repo=Depends(get_lote_repository),
):
    """
    Consulta el estado de procesamiento de un lote de transacciones

    Args:
        lote_id: ID del lote a consultar

    Returns:
        Estado del lote con porcentaje de progreso
    """
    use_case = ConsultarEstadoLoteUseCase(lote_repo=lote_repo)
    lote_status = await use_case.execute(lote_id=lote_id)

    if not lote_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lote {lote_id} no encontrado",
        )

    # Verificar que el lote pertenece al usuario
    lote = await lote_repo.get_by_id(lote_id)
    if lote.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a este lote",
        )

    return lote_status
