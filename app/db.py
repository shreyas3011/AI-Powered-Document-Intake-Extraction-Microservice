

import os
from datetime import datetime
import asyncio
import uuid
from types import SimpleNamespace

USE_IN_MEMORY = False
documents_coll = None

try:
   
    from motor.motor_asyncio import AsyncIOMotorClient

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "ocr_microservice")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    documents_coll = db["documents"]
    
    documents_coll.__dict__["_is_motor_collection"] = True

except Exception as exc:
   
    USE_IN_MEMORY = True

    class InMemoryCollection:
        def __init__(self):
            self._store = {}
        
        async def insert_one(self, doc):
            
            created_id = uuid.uuid4().hex
            
            record = dict(doc)
            record["_id"] = created_id
            
            if "uploaded_at" not in record:
                record["uploaded_at"] = datetime.utcnow()
            self._store[created_id] = record
            
            return SimpleNamespace(inserted_id=created_id)
        async def find_one(self, query):
            
            if not query:
                return None
           
            if "_id" in query:
                _id = query["_id"]
                return self._store.get(str(_id))
            
            for k, v in self._store.items():
                if k == str(query) or v.get("id") == str(query) or v.get("id") == query:
                    return v
           
            if "id" in query:
                return self._store.get(str(query["id"]))
            return None
        
        async def all(self):
            return list(self._store.values())

    documents_coll = InMemoryCollection()
    documents_coll._is_in_memory = True


__all__ = ("documents_coll", "USE_IN_MEMORY")
