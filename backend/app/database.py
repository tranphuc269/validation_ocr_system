from pymongo import MongoClient, ASCENDING
from pymongo.database import Database

from .config import settings


client: MongoClient | None = None
db: Database | None = None


def get_db() -> Database:
    global client, db
    if client is None:
        client = MongoClient(settings.mongo_url)
        db = client[settings.mongo_db]
    assert db is not None
    return db


def init_db() -> None:
    # ensure indexes and collections
    database = get_db()
    database["projects"].create_index([("name", ASCENDING)], unique=True)
    database["documents"].create_index([("project_id", ASCENDING)])
    database["uploads"].create_index([("document_id", ASCENDING)])
    database["validation_results"].create_index([("document_id", ASCENDING)])
    database["validation_results"].create_index([("created_at", ASCENDING)])
    database["validation_jobs"].create_index([("document_id", ASCENDING)])
    database["validation_jobs"].create_index([("status", ASCENDING)])
    database["validation_jobs"].create_index([("created_at", ASCENDING)])
    database["logs"].create_index([("created_at", ASCENDING)])


