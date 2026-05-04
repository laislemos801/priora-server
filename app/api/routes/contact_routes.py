from fastapi import APIRouter
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
def create_contact(data: CreateContactRequest):
    return create_contact_service(data.dict())


@router.get("/case/{caso_id}")
def list_contacts(caso_id: str):
    return list_contacts_service(caso_id)


@router.patch("/{contato_id}")
def update_contact(contato_id: str, data: UpdateContactRequest):
    return update_contact_service(
        contato_id,
        data.dict(exclude_unset=True)
    )


@router.delete("/case/{caso_id}/{contato_id}")
def delete_contact(caso_id: str, contato_id: str):
    return delete_contact_service(caso_id, contato_id)