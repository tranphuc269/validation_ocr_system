from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, Dict, Tuple


def extract_text_fields(ocr_json: Dict[str, Any]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    info = ocr_json.get("information")
    if not isinstance(info, list) or not info:
        return fields
    first = info[0]
    if not isinstance(first, dict):
        return fields
    for key, meta in first.items():
        if isinstance(meta, dict) and meta.get("type") == "text":
            value = meta.get("value")
            if isinstance(value, (str, int, float)):
                fields[key] = str(value)
    return fields


def string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").strip(), (b or "").strip()).ratio()


def compare_fields(user_fields: Dict[str, str], ocr_fields: Dict[str, str]) -> Tuple[dict, float]:
    results: dict[str, float] = {}
    scores: list[float] = []
    for key, user_val in user_fields.items():
        ocr_val = ocr_fields.get(key, "")
        score = string_similarity(user_val, ocr_val)
        results[key] = score
        scores.append(score)
    overall = sum(scores) / len(scores) if scores else 0.0
    return results, overall


