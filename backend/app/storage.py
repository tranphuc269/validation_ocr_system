from __future__ import annotations

from pathlib import Path
from typing import Optional
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi.responses import FileResponse, StreamingResponse

from .config import settings


class StorageService:
    """Handles file storage for both local filesystem and MinIO (S3-compatible)."""

    MINIO_PREFIX = "minio://"

    def __init__(self) -> None:
        self.backend = settings.storage_backend.upper()
        if self.backend not in {"LOCAL", "MINIO"}:
            raise ValueError("Unsupported storage backend: %s" % self.backend)

        if self.backend == "MINIO":
            if not settings.minio_endpoint or not settings.minio_bucket:
                raise ValueError("MINIO backend requires endpoint and bucket configuration")
            self.bucket = settings.minio_bucket
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.minio_endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                region_name=settings.minio_region,
                use_ssl=settings.minio_secure,
            )
            # Ensure bucket exists
            self._ensure_bucket()

    # ---------- Utility helpers ----------
    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def _local_path(self, key: str) -> Path:
        return Path(settings.storage_dir) / key

    def _is_minio(self, identifier: str) -> bool:
        return identifier.startswith(self.MINIO_PREFIX)

    def _key_from_identifier(self, identifier: str) -> str:
        return identifier[len(self.MINIO_PREFIX) :]

    def _get_date_prefix(self) -> str:
        """Get date prefix in dd-mm-yyyy format"""
        return datetime.utcnow().strftime("%d-%m-%Y")

    def _make_key_with_date(self, subfolder: str, filename: str) -> str:
        """Create key with date prefix: dd-mm-yyyy/subfolder/filename"""
        date_prefix = self._get_date_prefix()
        return f"{date_prefix}/{subfolder}/{filename}"

    def _make_identifier(self, key: str) -> str:
        if self.backend == "MINIO":
            return f"{self.MINIO_PREFIX}{key}"
        return str(self._local_path(key))

    def _has_date_prefix(self, key: str) -> bool:
        """Check if key already has date prefix (dd-mm-yyyy format)"""
        parts = key.split("/")
        if not parts:
            return False
        first_part = parts[0]
        # Check if first part matches dd-mm-yyyy format
        try:
            datetime.strptime(first_part, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    # ---------- Save operations ----------
    def save_bytes(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        """Save bytes. Key format: subfolder/filename (will auto-add date prefix)"""
        # If key doesn't have date prefix, add it
        if not self._has_date_prefix(key):
            # Extract subfolder and filename
            parts = key.split("/", 1)
            if len(parts) == 2:
                subfolder, filename = parts
            else:
                # Default to uploads if no subfolder specified
                subfolder = "uploads"
                filename = key
            key = self._make_key_with_date(subfolder, filename)
        
        if self.backend == "MINIO":
            args = {
                "Bucket": self.bucket,
                "Key": key,
                "Body": data,
            }
            if content_type:
                args["ContentType"] = content_type
            self.client.put_object(**args)
            return self._make_identifier(key)

        path = self._local_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def save_text(self, key: str, text: str, content_type: Optional[str] = "application/json") -> str:
        return self.save_bytes(key, text.encode("utf-8"), content_type=content_type)

    # ---------- Read operations ----------
    def read_bytes(self, identifier: str) -> bytes:
        if self._is_minio(identifier):
            key = self._key_from_identifier(identifier)
            obj = self.client.get_object(Bucket=self.bucket, Key=key)
            return obj["Body"].read()

        path = Path(identifier)
        return path.read_bytes()

    def read_text(self, identifier: str) -> str:
        return self.read_bytes(identifier).decode("utf-8")

    # ---------- Response helpers ----------
    def file_response(self, identifier: str, download_name: Optional[str] = None):
        if self._is_minio(identifier):
            key = self._key_from_identifier(identifier)
            obj = self.client.get_object(Bucket=self.bucket, Key=key)

            def iter_chunks():
                try:
                    for chunk in iter(lambda: obj["Body"].read(8192), b""):
                        if chunk:
                            yield chunk
                finally:
                    obj["Body"].close()

            return StreamingResponse(
                iter_chunks(),
                media_type=obj.get("ContentType", "application/octet-stream"),
                headers={
                    "Content-Disposition": f"attachment; filename={download_name}" if download_name else "attachment",
                },
            )

        path = Path(identifier)
        if not download_name:
            download_name = path.name
        return FileResponse(path, filename=download_name)


storage_service = StorageService()

