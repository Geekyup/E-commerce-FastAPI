from pathlib import Path
from fastapi import UploadFile
from PIL import Image
from io import BytesIO
import uuid
import json

MEDIA_DIR = Path("media")
MEDIA_URL = "/media"

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


async def save_upload_file(
    file: UploadFile,
    folder: str = "products",
    max_size: tuple[int, int] = (1920, 1920),
) -> str:

    # Проверка типа файла
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError("Недопустимый тип файла")

    # Создаём папку
    upload_dir = MEDIA_DIR / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Читаем файл
    contents = await file.read()

    try:
        # Открываем изображение
        image = Image.open(BytesIO(contents)).convert("RGB")

        # Сжимаем
        image.thumbnail(max_size)

        # Генерируем имя
        filename = f"{uuid.uuid4().hex}.jpg"

        # Путь сохранения
        file_path = upload_dir / filename

        # Сохраняем
        image.save(
            file_path,
            "JPEG",
            quality=85,
            optimize=True,
        )

        return f"{MEDIA_URL}/{folder}/{filename}"

    except Exception as e:
        raise ValueError(f"Ошибка обработки изображения: {e}")


def delete_upload_file(file_path: str) -> bool:
    try:
        path = MEDIA_DIR / file_path.replace(MEDIA_URL + "/", "")
        path.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def parse_images_json(images_json: str) -> list[str]:
    if not images_json:
        return []

    try:
        return json.loads(images_json)
    except json.JSONDecodeError:
        return []


def images_to_json(images: list[str]) -> str:
    return json.dumps(images)