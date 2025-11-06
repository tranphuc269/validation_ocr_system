import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pymongo.database import Database

from ..config import settings
from ..database import get_db
from .. import crud, schemas
from ..utils.validation import extract_text_fields


router = APIRouter()


@router.post("/", response_model=schemas.DocumentOut)
def create_document(payload: schemas.DocumentCreate, db: Database = Depends(get_db)):
    project = crud.get_project(db, str(payload.project_id)) if isinstance(payload.project_id, str) else crud.get_project(db, payload.project_id)  # type: ignore
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.create_document(db, payload)


@router.patch("/{doc_id}", response_model=schemas.DocumentOut)
def update_document(doc_id: str, payload: schemas.DocumentUpdate, db: Database = Depends(get_db)):
    doc = crud.update_document(db, doc_id, payload)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/", response_model=list[schemas.DocumentOut])
def list_documents(project_id: str | None = None, db: Database = Depends(get_db)):
    return crud.list_documents(db, project_id)


@router.get("/{doc_id}", response_model=schemas.DocumentOut)
def get_document(doc_id: str, db: Database = Depends(get_db)):
    doc = crud.get_document_raw(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return crud.serialize_document(doc)  # type: ignore


@router.post("/{doc_id}/sample-json", response_model=schemas.DocumentOut)
async def upload_sample_json(doc_id: str, sample: UploadFile = File(...), db: Database = Depends(get_db)):
    if not sample.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Sample must be a JSON file")
    doc = crud.get_document_raw(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content = await sample.read()
    # Validate JSON
    try:
        _ = json.loads(content.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON content")

    out_path = Path(settings.storage_dir) / "samples" / f"doc_{doc_id}_sample.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(content)
    updated = crud.set_document_sample_json_path(db, doc_id, str(out_path))
    if not updated:
        raise HTTPException(status_code=404, detail="Document not found")
    serialized = crud.serialize_document(updated)
    if not serialized:
        raise HTTPException(status_code=500, detail="Failed to serialize document")
    return serialized


@router.get("/{doc_id}/text-fields", response_model=list[str])
def get_text_fields(doc_id: str, db: Database = Depends(get_db)):
    doc = crud.get_document_raw(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    sample_path = doc.get("sample_json_path")
    if not sample_path:
        raise HTTPException(status_code=400, detail="Sample JSON not uploaded for document")
    try:
        parsed = json.loads(Path(sample_path).read_text(encoding="utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid sample JSON content")
    fields_map = extract_text_fields(parsed)
    return list(fields_map.keys())


@router.post("/{doc_id}/upload", response_model=schemas.UploadOut)
async def upload_file(doc_id: str, file: UploadFile = File(...), db: Database = Depends(get_db)):
    doc = crud.get_document_raw(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    ext = Path(file.filename).suffix.lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    content = await file.read()
    out_path = Path(settings.storage_dir) / "uploads" / f"doc_{doc_id}_{file.filename}"
    out_path.write_bytes(content)
    return crud.create_upload(db, doc_id, str(out_path))


@router.post("/{upload_id}/user-input", response_model=schemas.UploadOut)
async def upload_user_input(upload_id: str, form_json: UploadFile = File(...), db: Database = Depends(get_db)):
    if not form_json.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="User input must be a JSON file")
    content = await form_json.read()
    # Validate JSON
    try:
        _ = json.loads(content.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON content")
    out_path = Path(settings.storage_dir) / "user_inputs" / f"upload_{upload_id}_user.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(content)
    updated = crud.set_upload_user_input(db, upload_id, str(out_path))
    if not updated:
        raise HTTPException(status_code=404, detail="Upload not found")
    serialized = crud.serialize_upload(updated)
    if not serialized:
        raise HTTPException(status_code=500, detail="Failed to serialize upload")
    return serialized


@router.get("/{doc_id}/uploads", response_model=list[schemas.UploadOut])
def list_uploads(doc_id: str, db: Database = Depends(get_db)):
    items = crud.list_uploads_by_document(db, doc_id)
    # serialize
    out: list[schemas.UploadOut] = []
    for it in items:
        out.append(
            schemas.UploadOut(
                id=str(it.get("_id")),
                document_id=it.get("document_id"),
                file_path=it.get("file_path"),
                user_input_json_path=it.get("user_input_json_path"),
                created_at=it.get("created_at"),
            )
        )
    return out


