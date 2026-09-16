from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.services.bayes_service import run_bayes_preview_service

router = APIRouter(prefix="/bayes", tags=["Bayes"])


@router.post("/preview/{caso_id}")
def preview_bayes(caso_id: str, current_user_id: str = Depends(get_current_user_id)):
    return run_bayes_preview_service(current_user_id, caso_id)