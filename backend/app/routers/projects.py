from fastapi import APIRouter, Depends
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


