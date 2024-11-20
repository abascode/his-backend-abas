from fastapi import HTTPException, UploadFile
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable
from fastapi import UploadFile

def get_file_extension(file: UploadFile) -> str:
    filename = file.filename
    return filename.split(".")[-1] if "." in filename else ""

def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path


def handle_upload_file(
    upload_file: UploadFile, handler: Callable[[Path], None]
) -> None:
    tmp_path = save_upload_file_tmp(upload_file)
    try:
        handler(tmp_path)  
    finally:
        tmp_path.unlink()
        
def clear_directory(target: Path):
    if not target.is_dir():
        raise ValueError(f"The provided path '{target}' is not a directory.")

    for item in target.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()  
            elif item.is_dir():
                for sub_item in item.iterdir():
                    sub_item.unlink()  
                item.rmdir()  
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))