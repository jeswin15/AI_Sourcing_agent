import os
import logging
from src.utils.config import Config
from src.database.json_store import JSONStore
from src.database.mongo_client import MongoDBClient

logger = logging.getLogger("database.factory")

def get_db():
    """
    Returns the database client based on environment configuration.
    Defaults to JSONStore if database type is not specified or set to 'local_json'.
    """
    db_type = os.getenv("DATABASE_TYPE", "local_json").lower()
    
    if db_type == "mongodb":
        client = MongoDBClient()
        if client.is_connected:
            return client
        else:
            logger.warning("Falling back to JSON Store: MongoDB connection failed.")
            return JSONStore()
    
    return JSONStore()
