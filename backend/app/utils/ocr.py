from typing import Any, Dict

from io import BytesIO
import requests


def call_ocr(ocr_url: str, filename: str, file_bytes: bytes, timeout: int = 60) -> Dict[str, Any]:
    buffer = BytesIO(file_bytes)
    files = {"file": (filename, buffer, "application/octet-stream")}
    resp = requests.post(ocr_url, files=files, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


