from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    primeiroNome: str
    sobrenome: str
    senha: str


class LoginRequest(BaseModel):
    email: EmailStr


class RecoverRequest(BaseModel):
    email: EmailStr
    token: str


class ResetPasswordRequest(BaseModel):
    token: str
    novaSenha: str