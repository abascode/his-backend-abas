from google.cloud import storage
from contextlib import contextmanager
from fastapi import UploadFile


class GoogleStorageConfig:
    def __init__(self, path, filename, bucket):
        self.path = path
        self.filename = filename
        self.bucket = bucket


class StorageService:
    def __init__(self):
        self.client = storage.Client()

    @contextmanager
    def timeout(self, seconds):
        import signal

        def handler(signum, frame):
            raise TimeoutError()

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)

    def upload(self, file: UploadFile, config: GoogleStorageConfig) -> str:

        with self.timeout(50):
            bucket = self.client.bucket(config.bucket)
            blob = bucket.blob(f"temp/part-price/{config.path}/{config.filename}")
            blob.upload_from_file(file.file, content_type=file.content_type)
        return f"https://storage.googleapis.com/{config.bucket}/temp/part-price/{config.path}/{config.filename}"

    def download_file(self, bucket, path):
        with self.timeout(50):
            bucket = self.client.bucket(bucket)
            blob = bucket.blob(path)
            content = blob.download_as_bytes()
        return content

    def move_file(self, from_bucket, from_path, to_bucket, to_path):
        with self.timeout(50):
            source_bucket = self.client.bucket(from_bucket)
            source_blob = source_bucket.blob(from_path)
            destination_bucket = self.client.bucket(to_bucket)
            source_bucket.copy_blob(source_blob, destination_bucket, to_path)
            source_blob.delete()
        return

    def move_temp_file(self, path):
        with self.timeout(50):
            bucket = path.split("/")[3]
            prefix = f"https://storage.googleapis.com/{bucket}/"
            from_path = path.replace(prefix, "")
            to_path = from_path.replace("temp/", "")
            if from_path.startswith("temp/"):
                self.move_file(bucket, from_path, bucket, to_path)
        return f"{prefix}{to_path}"

    def delete_file(self, path):
        bucket = path.split("/")[3]
        prefix = f"https://storage.googleapis.com/{bucket}/"
        from_path = path.replace(prefix, "")
        to_path = f"deleted/{from_path}"
        self.move_file(bucket, from_path, bucket, to_path)
        return f"{prefix}{to_path}"

    def retrieve_file(self, path):
        bucket = path.split("/")[3]
        prefix = f"https://storage.googleapis.com/{bucket}/"
        from_path = path.replace(prefix, "")
        to_path = from_path.replace("deleted/", "")
        self.move_file(bucket, from_path, bucket, to_path)
        return f"{prefix}{to_path}"

    def generate_presigned_url(self, url):
        bucket = url.split("/")[3]
        prefix = f"https://storage.googleapis.com/{bucket}/"
        path = url.replace(prefix, "")
        blob = self.client.bucket(bucket).blob(path)
        url = blob.generate_signed_url(version="v4", expiration=3 * 60, method="GET")
        return url
