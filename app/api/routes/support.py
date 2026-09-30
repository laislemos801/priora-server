from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from app.services.support_service import send_support_service


router = APIRouter(
    prefix="/support",
    tags=["Support"]
)


class SupportRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    message: str


@router.post("")
async def send_support(request: SupportRequest):
    return await send_support_service(
        first_name=request.firstName,
        last_name=request.lastName,
        email=request.email,
        message=request.message
    )