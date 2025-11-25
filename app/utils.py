# app/utils.py
import tempfile
from fastapi import UploadFile
from pathlib import Path
import shutil

async def save_upload_tmp(upload_file: UploadFile) -> str:
    suffix = Path(upload_file.filename).suffix or ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tf:
        temp_name = tf.name
        
        content = await upload_file.read()
        tf.write(content)
    return temp_name
