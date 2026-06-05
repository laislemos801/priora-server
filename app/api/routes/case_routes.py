from fastapi import APIRouter
from app.services.case_service import (
    create_case_service,
    get_cases_service,
    update_uncertainty_service,
    get_case_service,
    update_case_service,
    delete_case_service
)

from app.schemas.case_schema import (
    CreateCaseRequest,
    UpdateUncertaintyRequest,
    UpdateCaseRequest
)

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/", status_code=201)
def create_case(data: CreateCaseRequest):
    return create_case_service(
        data.userId,
        data.dict()
    )


@router.get("/user/{user_id}")
def get_cases(user_id: str):
    return get_cases_service(user_id)


@router.get("/{caso_id}")
def get_case(caso_id: str):
    return get_case_service(caso_id)


@router.patch("/{caso_id}/uncertainty")
def update_uncertainty(caso_id: str, data: UpdateUncertaintyRequest):
    return update_uncertainty_service(
        caso_id,
        data.incerteza
    )


@router.patch("/{caso_id}")
def update_case_route(caso_id: str, data: UpdateCaseRequest):
    return update_case_service(
        caso_id,
        data.dict()
    )


@router.delete("/{caso_id}")
def delete_case_route(caso_id: str):
    return delete_case_service(caso_id)