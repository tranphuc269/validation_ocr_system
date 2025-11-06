from typing import Optional
from datetime import datetime

from pymongo.database import Database
from bson import ObjectId

from . import schemas


def _oid(val: int | str) -> ObjectId:
    if isinstance(val, ObjectId):
        return val
    if isinstance(val, int):
        # For simplicity, we store numeric IDs ourselves; but better to use ObjectIds.
        # Here we convert ints to deterministic ObjectId-like strings is non-trivial; instead we will store ints directly.
        raise ValueError("Numeric IDs not supported; use string/ObjectId")
    return ObjectId(val)


def create_project(db: Database, payload: schemas.ProjectCreate) -> dict:
    doc = {"name": payload.name, "created_at": datetime.utcnow()}
    result = db["projects"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_project(doc)


def list_projects(db: Database) -> list[dict]:
    items = db["projects"].find().sort("created_at", -1)
    return [serialize_project(it) for it in items]


def get_project(db: Database, project_id: str) -> Optional[dict]:
    it = db["projects"].find_one({"_id": _oid(project_id)})
    return serialize_project(it) if it else None


def create_document(db: Database, payload: schemas.DocumentCreate) -> dict:
    doc = {
        "project_id": payload.project_id,
        "name": payload.name,
        "ocr_url": payload.ocr_url,
        "sample_json_path": None,
        "created_at": datetime.utcnow(),
    }
    res = db["documents"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize_document(doc)


def update_document(db: Database, doc_id: str, payload: schemas.DocumentUpdate) -> Optional[dict]:
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        it = db["documents"].find_one({"_id": _oid(doc_id)})
        return serialize_document(it) if it else None
    it = db["documents"].find_one_and_update({"_id": _oid(doc_id)}, {"$set": updates}, return_document=True)
    return serialize_document(it) if it else None


def list_documents(db: Database, project_id: Optional[str] = None) -> list[dict]:
    q: dict = {}
    if project_id is not None:
        q["project_id"] = project_id
    items = db["documents"].find(q).sort("created_at", -1)
    return [serialize_document(it) for it in items]


def set_document_sample_json_path(db: Database, doc_id: str, path: str) -> Optional[dict]:
    it = db["documents"].find_one_and_update({"_id": _oid(doc_id)}, {"$set": {"sample_json_path": path}}, return_document=True)
    return it  # Return raw dict, not serialized


def create_upload(db: Database, document_id: str, file_path: str) -> dict:
    doc = {
        "document_id": document_id,
        "file_path": file_path,
        "user_input_json_path": None,
        "created_at": datetime.utcnow(),
    }
    res = db["uploads"].insert_one(doc)
    doc["_id"] = res.inserted_id
    return serialize_upload(doc)


def set_upload_user_input(db: Database, upload_id: str, user_input_path: str) -> Optional[dict]:
    it = db["uploads"].find_one_and_update({"_id": _oid(upload_id)}, {"$set": {"user_input_json_path": user_input_path}}, return_document=True)
    return it  # Return raw dict, not serialized


def get_document_raw(db: Database, document_id: str) -> Optional[dict]:
    return db["documents"].find_one({"_id": _oid(document_id)})


def get_upload_raw(db: Database, upload_id: str) -> Optional[dict]:
    return db["uploads"].find_one({"_id": _oid(upload_id)})


def list_uploads_by_document(db: Database, document_id: str) -> list[dict]:
    """Get all uploads for a document that have user_input_json_path set"""
    items = db["uploads"].find({
        "document_id": document_id,
        "user_input_json_path": {"$ne": None}
    }).sort("created_at", -1)
    return list(items)


def add_validation_result(
    db: Database,
    *,
    document_id: str,
    upload_id: str,
    field_name: str,
    user_value: str,
    ocr_value: str,
    accuracy: float,
) -> dict:
    vr = {
        "document_id": document_id,
        "upload_id": upload_id,
        "field_name": field_name,
        "user_value": user_value,
        "ocr_value": ocr_value,
        "accuracy": accuracy,
        "created_at": datetime.utcnow(),
    }
    res = db["validation_results"].insert_one(vr)
    vr["_id"] = res.inserted_id
    return vr


def log_event(db: Database, level: str, message: str, context: Optional[str] = None) -> dict:
    entry = {"level": level, "message": message, "context": context, "created_at": datetime.utcnow()}
    res = db["logs"].insert_one(entry)
    entry["_id"] = res.inserted_id
    return entry


def create_validation_job(db: Database, document_id: str) -> dict:
    """Create a new validation job"""
    job = {
        "document_id": document_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "error": None,
        "result": None,
        "total_uploads": None,
        "processed_uploads": None,
    }
    res = db["validation_jobs"].insert_one(job)
    job["_id"] = res.inserted_id
    return job


def get_validation_job(db: Database, job_id: str) -> Optional[dict]:
    """Get validation job by ID"""
    return db["validation_jobs"].find_one({"_id": _oid(job_id)})


def update_validation_job_status(
    db: Database,
    job_id: str,
    status: str,
    error: Optional[str] = None,
    result: Optional[dict] = None,
    total_uploads: Optional[int] = None,
    processed_uploads: Optional[int] = None,
) -> Optional[dict]:
    """Update validation job status"""
    updates: dict = {"status": status}
    
    # Set started_at when status changes to running (only if not already set)
    if status == "running":
        existing = db["validation_jobs"].find_one({"_id": _oid(job_id)})
        if existing and not existing.get("started_at"):
            updates["started_at"] = datetime.utcnow()
    
    if status in ("completed", "failed"):
        updates["completed_at"] = datetime.utcnow()
    if error is not None:
        updates["error"] = error
    if result is not None:
        updates["result"] = result
    if total_uploads is not None:
        updates["total_uploads"] = total_uploads
    if processed_uploads is not None:
        updates["processed_uploads"] = processed_uploads
    
    it = db["validation_jobs"].find_one_and_update({"_id": _oid(job_id)}, {"$set": updates}, return_document=True)
    return it


def serialize_validation_job(it: Optional[dict]) -> Optional[dict]:
    """Serialize validation job for API response"""
    if not it:
        return None
    return {
        "job_id": serialize_id(it.get("_id")),
        "document_id": it.get("document_id"),
        "status": it.get("status"),
        "created_at": it.get("created_at"),
        "started_at": it.get("started_at"),
        "completed_at": it.get("completed_at"),
        "error": it.get("error"),
        "total_uploads": it.get("total_uploads"),
        "processed_uploads": it.get("processed_uploads"),
    }


def serialize_id(v) -> str:
    return str(v) if isinstance(v, ObjectId) else v


def serialize_project(it: Optional[dict]) -> Optional[dict]:
    if not it:
        return None
    proj_id = it.get("_id")
    if proj_id is None:
        return None
    return {"id": serialize_id(proj_id), "name": it.get("name"), "created_at": it.get("created_at")}


def serialize_document(it: Optional[dict]) -> Optional[dict]:
    if not it:
        return None
    doc_id = it.get("_id")
    if doc_id is None:
        return None
    return {
        "id": serialize_id(doc_id),
        "project_id": it.get("project_id"),
        "name": it.get("name"),
        "ocr_url": it.get("ocr_url"),
        "sample_json_path": it.get("sample_json_path"),
        "created_at": it.get("created_at"),
    }


def serialize_upload(it: Optional[dict]) -> Optional[dict]:
    if not it:
        return None
    upload_id = it.get("_id")
    if upload_id is None:
        return None
    return {
        "id": serialize_id(upload_id),
        "document_id": it.get("document_id"),
        "file_path": it.get("file_path"),
        "user_input_json_path": it.get("user_input_json_path"),
        "created_at": it.get("created_at"),
    }


