from typing import Optional
from ...domain.ports import LoteTransaccionRepositoryPort
from ..dto import LoteStatusDTO


class ConsultarEstadoLoteUseCase:
    def __init__(self, lote_repo: LoteTransaccionRepositoryPort):
        self.lote_repo = lote_repo

    async def execute(self, lote_id: int) -> Optional[LoteStatusDTO]:
        lote = await self.lote_repo.get_by_id(lote_id)
        if not lote:
            return None

        return LoteStatusDTO(
            lote_id=lote.id,
            estado=lote.estado.value,
            total_registros=lote.total_registros,
            registros_procesados=lote.registros_procesados,
            porcentaje_procesado=lote.porcentaje_procesado,
            created_at=lote.created_at,
            updated_at=lote.updated_at,
        )
