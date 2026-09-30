from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


async def send_recovery_email(email: str, token: str):
    frontend_url = os.getenv("FRONTEND_URL")
    link = f"{frontend_url}/recover/new-password?token={token}"

    message = MessageSchema(
        subject="Recuperação de senha",
        recipients=[email],
        body=f"""
Clique no link abaixo para redefinir sua senha:

{link}
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_support_email(
    first_name: str,
    last_name: str,
    email: str,
    message_text: str
):
    support_email = os.getenv("SUPPORT_EMAIL")

    message = MessageSchema(
        subject=f"[Suporte] {first_name} {last_name}",
        recipients=[support_email],
        reply_to=[email],
        body=f"""
Nova mensagem recebida pelo formulário de contato.

Nome: {first_name} {last_name}
Email: {email}

Mensagem:
{message_text}
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)