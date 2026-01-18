from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings

_client: MongoClient | None = None
_db: Database | None = None


def get_database() -> Database:
    """Get the pet store database (lazy initialization)."""
    global _client, _db
    if _db is None:
        _client = MongoClient(settings.mongodb_uri)
        _db = _client.pet_store_db
    return _db


def get_transactions_collection():
    """Get the transactions collection (shared by all pet-order instances)."""
    return get_database().transactions
