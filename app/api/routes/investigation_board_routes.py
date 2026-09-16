from fastapi import APIRouter, HTTPException, UploadFile, File
import traceback

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

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/{caso_id}/board/images", status_code=201)
async def upload_board_image_route(caso_id: str, file: UploadFile = File(...)):
    file_bytes = await file.read()

    try:
        url = await upload_board_image_service(
            caso_id,
            file_bytes,
            file.content_type
        )
        return {"url": url}

    except Exception as e:
        import traceback

        traceback.print_exc()
        print("ERRO REAL:", repr(e))

        raise
