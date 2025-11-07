from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from ..database import get_db
from .. import crud, schemas


router = APIRouter()


@router.post("/", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Database = Depends(get_db)):
    return crud.create_project(db, payload)


@router.get("/", response_model=list[schemas.ProjectOut])
def list_projects(db: Database = Depends(get_db)):
    return crud.list_projects(db)


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: str, payload: schemas.ProjectUpdate, db: Database = Depends(get_db)):
    project = crud.update_project(db, project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Database = Depends(get_db)):
    from ..storage import storage_service
    # Get all documents in this project to delete their files
    docs = db["documents"].find({"project_id": project_id})
    for doc in docs:
        doc_id = str(doc["_id"])
        # Delete sample JSON if exists
        if doc.get("sample_json_path"):
            try:
                storage_service.delete_file(doc["sample_json_path"])
            except Exception:
                pass
        # Get all uploads for this document
        uploads = db["uploads"].find({"document_id": doc_id})
        for upload in uploads:
            # Delete uploaded file
            if upload.get("file_path"):
                try:
                    storage_service.delete_file(upload["file_path"])
                except Exception:
                    pass
            # Delete user input JSON if exists
            if upload.get("user_input_json_path"):
                try:
                    storage_service.delete_file(upload["user_input_json_path"])
                except Exception:
                    pass
    
    success = crud.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


