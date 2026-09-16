from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.schemas.contact_schema import (
    CreateContactRequest,
    UpdateContactRequest
)
from app.services.contact_service import (
    create_contact_service,
    list_contacts_service,
    update_contact_service,
    delete_contact_service
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("/", status_code=201)
def create_contact(data: CreateContactRequest, current_user_id: str = Depends(get_current_user_id)):
    return create_contact_service(current_user_id, data.dict())


@router.get("/case/{caso_id}")
def list_contacts(caso_id: str, current_user_id: str = Depends(get_current_user_id)):
    return list_contacts_service(current_user_id, caso_id)


@router.patch("/{contato_id}")
def update_contact(contato_id: str, data: UpdateContactRequest, current_user_id: str = Depends(get_current_user_id)):
    return update_contact_service(
        current_user_id,
        contato_id,
        data.dict(exclude_unset=True)
    )


@router.delete("/case/{caso_id}/{contato_id}")
def delete_contact(caso_id: str, contato_id: str, current_user_id: str = Depends(get_current_user_id)):
    return delete_contact_service(current_user_id, caso_id, contato_id)