from fastapi import APIRouter
from app.services.case_service import (
    create_case_service,
    get_cases_service,
    update_uncertainty_service
)

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/")
def create_case(data: dict):
    return create_case_service(data["userId"], data)


@router.get("/user/{user_id}")
def get_cases(user_id: str):
    return get_cases_service(user_id)


@router.patch("/{caso_id}/uncertainty")
def update_uncertainty(caso_id: str, data: dict):
    return update_uncertainty_service(caso_id, data["incerteza"])