from typing import Any, Dict, Optional

import requests


def call_ocr(ocr_url: str, file_path: str, timeout: int = 60) -> Dict[str, Any]:
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "application/octet-stream")}
        resp = requests.post(ocr_url, files=files, timeout=timeout)
        resp.raise_for_status()
        return resp.json()


