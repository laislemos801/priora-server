from fastapi import APIRouter, Depends

from app.api.routes.user_routes import get_current_user
from app.services.history_service import get_case_history_service


router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/cases/{caso_id}")
def get_case_history_route(
    caso_id: str,
    current_user=Depends(get_current_user)
):
    return get_case_history_service(
        current_user["id"],
        caso_id
    )
