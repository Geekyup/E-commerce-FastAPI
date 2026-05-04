import os
import uuid
from fastapi import HTTPException, UploadFile

UPLOAD_DIR = "media/products"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


async def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый формат. Разрешены: jpg, png, webp",
        )

    contents = await file.read()

    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Файл слишком большой. Максимум 5MB",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(contents)

    return f"/media/products/{filename}"


def delete_image_file(url: str) -> None:
    path = url.lstrip("/")
    if os.path.exists(path):
        os.remove(path)