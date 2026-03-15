import os
import shutil
from uuid import uuid4
from fastapi import UploadFile
from typing import List

UPLOAD_DIR = "media"

def upload_image(image: UploadFile, folder_name: str) -> str:
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    file_ext = image.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_ext}"

    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/media/{folder_name}/{filename}"

def upload_images(images: List[UploadFile], folder_name: str) -> List[str]:
    folder_path = os.path.join(UPLOAD_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    uploaded_urls = []

    for image in images:
        file_ext = image.filename.split(".")[-1]
        filename = f"{uuid4()}.{file_ext}"
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        uploaded_urls.append(f"/media/{folder_name}/{filename}")

    return uploaded_urls

def remove_image(file_path):
    if os.path.exists(file_path):
            os.remove(file_path)


