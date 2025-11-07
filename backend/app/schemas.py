from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = None


class ProjectOut(BaseModel):
    id: str
    name: str
    created_at: datetime


class DocumentCreate(BaseModel):
    project_id: str
    name: str
    ocr_url: Optional[str] = None


class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    ocr_url: Optional[str] = None


class DocumentOut(BaseModel):
    id: str
    project_id: str
    name: str
    ocr_url: Optional[str]
    sample_json_path: Optional[str]
    created_at: datetime


class UploadOut(BaseModel):
    id: str
    document_id: str
    file_path: str
    user_input_json_path: Optional[str]
    created_at: datetime


class ValidationRequest(BaseModel):
    document_id: str


class ValidationFieldResult(BaseModel):
    field_name: str
    user_value: str
    ocr_value: str
    accuracy: float = Field(ge=0.0, le=1.0)


class ValidationRunResult(BaseModel):
    results: list[ValidationFieldResult]
    overall_accuracy: float
    ocr_processing_time: Optional[float] = None
    ocr_raw: Optional[Any] = None


class ValidationUploadResult(BaseModel):
    upload_id: str
    results: list[ValidationFieldResult]
    overall_accuracy: float
    ocr_processing_time: Optional[float] = None
    error: Optional[str] = None


class ValidationDocumentResult(BaseModel):
    document_id: str
    upload_results: list[ValidationUploadResult]
    total_uploads: int
    successful_uploads: int
    failed_uploads: int


class ValidationJobCreate(BaseModel):
    document_id: str


class ValidationJobOut(BaseModel):
    job_id: str
    document_id: str
    status: str  # "pending", "running", "completed", "failed"
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    total_uploads: Optional[int] = None
    processed_uploads: Optional[int] = None


class ValidationJobResult(BaseModel):
    job_id: str
    status: str
    result: Optional[ValidationDocumentResult] = None
    error: Optional[str] = None


