import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pymongo.database import Database

from ..database import get_db
from .. import crud, schemas
from ..utils.ocr import call_ocr
from ..utils.validation import extract_text_fields, compare_fields


router = APIRouter()


def _validate_single_upload(
    db: Database,
    document: dict,
    upload: dict,
) -> schemas.ValidationUploadResult:
    """Validate a single upload and return results"""
    upload_id = str(upload.get("_id"))
    
    try:
        # Read user input JSON (already validated when uploaded)
        user_input_path = upload.get("user_input_json_path")
        if not user_input_path:
            return schemas.ValidationUploadResult(
                upload_id=upload_id,
                results=[],
                overall_accuracy=0.0,
                error="Upload has no user input JSON"
            )
        
        user_fields_obj: dict[str, Any] = json.loads(Path(user_input_path).read_text(encoding="utf-8"))

        # The user input JSON is expected to be a flat dict of key -> value from the generated form
        if not isinstance(user_fields_obj, dict):
            return schemas.ValidationUploadResult(
                upload_id=upload_id,
                results=[],
                overall_accuracy=0.0,
                error="User input JSON format invalid; expected an object"
            )
        user_text_fields: dict[str, str] = {k: str(v) for k, v in user_fields_obj.items()}

        # Call OCR service
        ocr_url = document.get("ocr_url")
        file_path = upload.get("file_path")
        if not ocr_url:
            return schemas.ValidationUploadResult(
                upload_id=upload_id,
                results=[],
                overall_accuracy=0.0,
                error="Document has no OCR URL configured"
            )
        
        # Mock path: use sample JSON if ocr_url == "mock"
        if str(ocr_url).lower() == "mock":
            sample_path = document.get("sample_json_path")
            if not sample_path:
                return schemas.ValidationUploadResult(
                    upload_id=upload_id,
                    results=[],
                    overall_accuracy=0.0,
                    error="Sample JSON not uploaded for document"
                )
            try:
                ocr_json = json.loads(Path(sample_path).read_text(encoding="utf-8"))
            except Exception as e:
                return schemas.ValidationUploadResult(
                    upload_id=upload_id,
                    results=[],
                    overall_accuracy=0.0,
                    error=f"Failed to read sample JSON: {e}"
                )
        else:
            try:
                ocr_json = call_ocr(ocr_url, file_path)
            except Exception as e:
                crud.log_event(db, "ERROR", f"OCR request failed for upload {upload_id}", context=str(e))
                return schemas.ValidationUploadResult(
                    upload_id=upload_id,
                    results=[],
                    overall_accuracy=0.0,
                    error=f"OCR service error: {e}"
                )

        # Extract text-only fields from OCR response
        ocr_text_fields = extract_text_fields(ocr_json)

        # Compare fields
        field_scores, overall = compare_fields(user_text_fields, ocr_text_fields)

        # Remove previous validation results for this upload so we only keep the latest run
        db["validation_results"].delete_many({"upload_id": upload_id})

        results: list[schemas.ValidationFieldResult] = []
        for key, user_val in user_text_fields.items():
            ocr_val = ocr_text_fields.get(key, "")
            score = field_scores.get(key, 0.0)
            # Persist per-field results
            crud.add_validation_result(
                db,
                document_id=str(document.get("_id")),
                upload_id=upload_id,
                field_name=key,
                user_value=user_val,
                ocr_value=ocr_val,
                accuracy=score,
            )
            results.append(
                schemas.ValidationFieldResult(
                    field_name=key, user_value=user_val, ocr_value=ocr_val, accuracy=score
                )
            )

        processing_time = None
        if isinstance(ocr_json, dict) and isinstance(ocr_json.get("processing_time"), (int, float)):
            processing_time = float(ocr_json["processing_time"])  # type: ignore

        return schemas.ValidationUploadResult(
            upload_id=upload_id,
            results=results,
            overall_accuracy=overall,
            ocr_processing_time=processing_time,
        )
    except Exception as e:
        crud.log_event(db, "ERROR", f"Validation error for upload {upload_id}", context=str(e))
        return schemas.ValidationUploadResult(
            upload_id=upload_id,
            results=[],
            overall_accuracy=0.0,
            error=f"Validation error: {e}"
        )


def _run_validation_task(job_id: str, document_id: str) -> None:
    """Background task to run validation"""
    from ..database import get_db as get_db_func
    
    db = get_db_func()
    
    try:
        # Update job status to running
        crud.update_validation_job_status(db, job_id, "running")
        
        document = crud.get_document_raw(db, document_id)
        if not document:
            crud.update_validation_job_status(db, job_id, "failed", error="Document not found")
            return
        
        # Get all uploads for this document that have user input
        uploads = crud.list_uploads_by_document(db, str(document.get("_id")))
        
        if not uploads:
            crud.update_validation_job_status(db, job_id, "failed", error="No uploads with user input found for this document")
            return
        
        total_uploads = len(uploads)
        crud.update_validation_job_status(db, job_id, "running", total_uploads=total_uploads, processed_uploads=0)
        
        # Validate each upload
        upload_results: list[schemas.ValidationUploadResult] = []
        for idx, upload in enumerate(uploads):
            result = _validate_single_upload(db, document, upload)
            upload_results.append(result)
            # Update progress
            crud.update_validation_job_status(db, job_id, "running", processed_uploads=idx + 1)
        
        successful = sum(1 for r in upload_results if r.error is None)
        failed = len(upload_results) - successful
        
        result_data = schemas.ValidationDocumentResult(
            document_id=str(document.get("_id")),
            upload_results=upload_results,
            total_uploads=len(upload_results),
            successful_uploads=successful,
            failed_uploads=failed,
        )
        
        # Save result and mark as completed
        crud.update_validation_job_status(
            db,
            job_id,
            "completed",
            result=result_data.model_dump(),
            processed_uploads=total_uploads,
        )
        
        crud.log_event(
            db,
            "INFO",
            f"Validation job {job_id} completed: {successful} successful, {failed} failed"
        )
    except Exception as e:
        crud.log_event(db, "ERROR", f"Validation job {job_id} failed", context=str(e))
        crud.update_validation_job_status(db, job_id, "failed", error=str(e))


@router.post("/run", response_model=schemas.ValidationJobOut)
def run_validation(
    payload: schemas.ValidationRequest,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db),
):
    """Start validation job for all uploads in a document (async)"""
    document = crud.get_document_raw(db, str(payload.document_id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if there are uploads with user input
    uploads = crud.list_uploads_by_document(db, str(document.get("_id")))
    if not uploads:
        raise HTTPException(status_code=400, detail="No uploads with user input found for this document")
    
    # Create validation job
    job = crud.create_validation_job(db, str(document.get("_id")))
    
    # Start background task
    job_id = str(job["_id"])
    background_tasks.add_task(_run_validation_task, job_id, str(document.get("_id")))
    
    return crud.serialize_validation_job(job)  # type: ignore


@router.get("/status/{job_id}", response_model=schemas.ValidationJobOut)
def get_validation_status(job_id: str, db: Database = Depends(get_db)):
    """Get validation job status"""
    job = crud.get_validation_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.serialize_validation_job(job)  # type: ignore


@router.get("/result/{job_id}", response_model=schemas.ValidationJobResult)
def get_validation_result(job_id: str, db: Database = Depends(get_db)):
    """Get validation job result"""
    job = crud.get_validation_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result = None
    if job.get("status") == "completed" and job.get("result"):
        result = schemas.ValidationDocumentResult(**job["result"])
    
    return schemas.ValidationJobResult(
        job_id=str(job["_id"]),
        status=job.get("status", "unknown"),
        result=result,
        error=job.get("error"),
    )


@router.get("/upload/{upload_id}/results", response_model=list[schemas.ValidationFieldResult])
def get_upload_validation_results(upload_id: str, db: Database = Depends(get_db)):
    """Get validation results for a specific upload"""
    results = db["validation_results"].find({"upload_id": upload_id}).sort("created_at", -1)
    out: list[schemas.ValidationFieldResult] = []
    seen_fields: set[str] = set()
    for r in results:
        field_name = r.get("field_name")
        if field_name in seen_fields:
            continue
        seen_fields.add(field_name)
        out.append(
            schemas.ValidationFieldResult(
                field_name=field_name,
                user_value=r.get("user_value"),
                ocr_value=r.get("ocr_value"),
                accuracy=r.get("accuracy"),
            )
        )
    return out


