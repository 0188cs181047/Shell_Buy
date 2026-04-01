import os
import shutil
from uuid import uuid4
from fastapi import UploadFile

UPLOAD_DIR = "media"

def save_file(file: UploadFile, folder: str = "knowledge"):
    """
    Save uploaded file and return (file_path, file_url, file_ext)
    """

    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

    file_ext = file.filename.split(".")[-1].lower()
    filename = f"{uuid4()}.{file_ext}"

    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/media/{folder}/{filename}"

    return file_path, file_url, file_ext