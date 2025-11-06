from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import projects, documents, validation, logs


app = FastAPI(title="Validation OCR System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(validation.router, prefix="/api/validation", tags=["validation"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


