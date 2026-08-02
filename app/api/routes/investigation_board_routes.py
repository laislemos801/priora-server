from fastapi import APIRouter, HTTPException, UploadFile, File

from app.services.investigation_board_service import (
    get_board_service,
    save_board_service,
)
from app.services.upload_service import upload_board_image_service
from app.schemas.investigation_board_schema import SaveBoardRequest

router = APIRouter(prefix="/cases", tags=["Quadro Investigativo"])


@router.get("/{caso_id}/board")
def get_board(caso_id: str):
    board = get_board_service(caso_id)

    if board is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")

    return board


@router.put("/{caso_id}/board")
def save_board(caso_id: str, data: SaveBoardRequest):
    try:
        return save_board_service(
            caso_id,
            [node.model_dump() for node in data.nodes],
            [edge.model_dump() for edge in data.edges],
        )
    except Exception as e:
        if "não encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail="Erro ao salvar o quadro investigativo.")


@router.post("/{caso_id}/board/images", status_code=201)
async def upload_board_image_route(caso_id: str, file: UploadFile = File(...)):
    """
    Recebe o arquivo de imagem (multipart/form-data), envia pro Supabase Storage
    a partir do backend, e devolve a URL pública pra ser usada no campo
    `data.imageUrl` de um node do tipo imageBox.
    """
    file_bytes = await file.read()

    try:
        url = await upload_board_image_service(caso_id, file_bytes, file.content_type)
    except ValueError as e:
        # erro de validação (tipo/tamanho do arquivo) — culpa do cliente
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao enviar a imagem para o Supabase.")

    return {"url": url}

