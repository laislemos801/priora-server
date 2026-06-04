from fastapi import APIRouter
from app.services.bayes_service import run_bayes_preview_service

router = APIRouter(prefix="/bayes", tags=["Bayes"])


@router.post("/preview/{caso_id}")
def preview_bayes(caso_id: str):
    return run_bayes_preview_service(caso_id)