import http
import os
import shutil
import uuid

from fastapi import File, HTTPException


def save_file(path: str, file: File) -> str:
    upload_dir = os.path.join(os.getcwd(), "storage/temp/{}".format(path))
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    extension = os.path.splitext(file.filename)[-1]
    file_name = str(uuid.uuid4()) + extension
    dest = os.path.join(upload_dir, file_name)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return dest.removeprefix(os.getcwd() + "/storage")


def move_file(from_path: str, to_path: str):
    base_path = os.path.join(os.getcwd(), "storage")
    to_dir = os.path.dirname(base_path + to_path)

    if not os.path.exists(to_dir):
        os.makedirs(to_dir)
    shutil.move(base_path + from_path, base_path + to_path)


def is_file_exist(path: str):
    return os.path.exists(os.path.join(os.getcwd(), "storage") + path)


def move_temp_file(path: str) -> str:
    if path.find("/temp") != 0:
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Temp file is not found",
        )
    if not is_file_exist(path):
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Temp file is not found",
        )

    move_file(path, path.removeprefix("/temp"))
    return path.removeprefix("/temp")


def delete_file(path: str):
    if not is_file_exist(path):
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="File is not found",
        )

    os.remove(os.path.join(os.getcwd(), "storage") + path)


def get_full_path(path: str) -> str:
    return os.path.join(os.getcwd(), "storage") + path
