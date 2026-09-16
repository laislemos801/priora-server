from app.database.supabase_storage import upload_board_image


async def upload_board_image_service(caso_id: str, file_bytes: bytes, content_type: str) -> str:
    return await upload_board_image(caso_id, file_bytes, content_type)
