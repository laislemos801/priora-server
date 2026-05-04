from pydantic import BaseModel, EmailStr


class InviteUserRequest(BaseModel):
    email: EmailStr
    casoId: str
    papel: str


class AcceptInviteRequest(BaseModel):
    userId: str
    casoId: str