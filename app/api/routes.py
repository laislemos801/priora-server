from fastapi import APIRouter
from app.services.investigation_service import rank_suspects

router = APIRouter()

@router.post("/rank")
def rank(evidence: dict):
    return rank_suspects(evidence)