# Validation OCR System

Full-stack platform to manage projects, documents, import OCR samples, upload files, capture user input, and validate OCR results.

## Tech
- Backend: FastAPI (Python), PyMongo, MongoDB
- Frontend: Vue
- Orchestration: Docker Compose

## Run
```bash
docker-compose up --build
```
- API: http://localhost:8000
- Health: http://localhost:8000/health

## API (high-level)
- POST /api/projects
- GET /api/projects
- POST /api/documents
- PATCH /api/documents/{doc_id}
- GET /api/documents?project_id=
- POST /api/documents/{doc_id}/sample-json (multipart file)
- POST /api/documents/{doc_id}/upload (multipart file: pdf/image)
- POST /api/documents/{upload_id}/user-input (multipart file: json)
- POST /api/validation/run (json: { document_id, upload_id })

## Storage
Mounted at `/data/storage` inside backend container:
- uploads/
- samples/
- user_inputs/

## Notes
- Only fields with `type = "text"` inside `information[0]` are considered during validation.
- Accuracy computed via difflib SequenceMatcher ratio in [0,1].

