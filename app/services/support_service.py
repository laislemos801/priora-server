from app.utils.email import send_support_email


async def send_support_service(
    first_name: str,
    last_name: str,
    email: str,
    message: str
):
    await send_support_email(
        first_name=first_name,
        last_name=last_name,
        email=email,
        message_text=message
    )

    return {
        "message": "Mensagem enviada com sucesso"
    }