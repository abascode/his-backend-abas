from fastapi import UploadFile


def get_file_extension(file: UploadFile) -> str:
    filename = file.filename
    return filename.split(".")[-1] if "." in filename else ""
