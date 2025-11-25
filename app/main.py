# app/main.py
import os
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Optional

from .ocr import extract_text_from_file
from .parsers import parse_page
from .utils import save_upload_tmp


load_dotenv()

app = FastAPI(
    title="OCR Microservice",
    description="AI-Powered Document Intake & Extraction Microservice. Extracts student and exam related information from PDFs and images.",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "OCR Microservice API",
        "endpoints": [
            "/upload - POST to upload and process documents",
            "/results/{doc_id} - GET to retrieve processed document data"
        ]
    }


MONGODB_URI = os.getenv("MONGODB_URI")  
MONGODB_DB = os.getenv("MONGODB_DB", "ocr")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "ocr_assignment")


client = None
db = None
collection = None

def get_collection():
    """Get or create the MongoDB collection on first access"""
    global client, db, collection
    if collection is None and MONGODB_URI:
        try:
            client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            db = client[MONGODB_DB]
            collection = db[MONGODB_COLLECTION]
            print("MongoDB client initialized (on first use)")
        except Exception as e:
            print(f"MongoDB client initialization failed: {e}")
            collection = None  
    return collection

@app.post("/upload")
async def upload_and_save(file: UploadFile = File(...)):
    
    if not file.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Only PDF, PNG, and JPG files are allowed")

   
    temp_file_path = await save_upload_tmp(file)

    try:
       
        pages_text, page_numbers = await extract_text_from_file(temp_file_path)

        
        pages = []
        for i, (text, page_num) in enumerate(zip(pages_text, page_numbers)):
           
            parsed_data = parse_page(text)

           
            parsed_fields = []
            for key, value in parsed_data.items():
                if value is not None:
                    parsed_fields.append({
                        "field_name": key,
                        "value": str(value) if isinstance(value, list) else value
                    })

            pages.append({
                "page_number": page_num,
                "text": text,
                "parsed": parsed_fields,
                "extracted_data": parsed_data
            })

        doc = {
            "_id": str(uuid.uuid4()),
            "filename": file.filename,
            "uploaded_at": datetime.utcnow(),
            "pages": pages
        }

        
        db_collection = get_collection()
        if db_collection is not None:
            try:
                await db_collection.insert_one(doc)
                return {"status": "saved", "id": doc["_id"], "message": "Document saved to database"}
            except Exception as db_error:
                print(f"Database save failed: {db_error}")
                
                return {"status": "processed", "id": doc["_id"], "message": "Document processed but not saved to database (DB error)"}
        else:
            
            return {"status": "processed", "id": doc["_id"], "message": "Document processed but not saved to database (DB unavailable)"}

    except Exception as e:
        import traceback
        error_details = str(e) + " | " + traceback.format_exc()
        print(f"Upload processing error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {error_details}")

    finally:
       
        try:
            os.remove(temp_file_path)
        except Exception:
            pass  


@app.get("/results/{doc_id}")
async def get_results(doc_id: str):
    """Fetch extracted and parsed data for a specific document by ID"""
    db_collection = get_collection()
    if db_collection is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")

    try:
        document = await db_collection.find_one({"_id": doc_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return {
            "id": document["_id"],
            "filename": document["filename"],
            "uploaded_at": document["uploaded_at"],
            "pages": document["pages"]
        }
    except Exception as e:
        import traceback
        error_details = str(e) + " | " + traceback.format_exc()
        print(f"Get results error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {error_details}")


@app.get("/documents")
async def list_documents():
    """List all document IDs and basic info"""
    db_collection = get_collection()
    if db_collection is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")

    try:
        documents = []
        async for doc in db_collection.find({}, {"_id": 1, "filename": 1, "uploaded_at": 1}):
            documents.append({
                "id": doc["_id"],
                "filename": doc["filename"],
                "uploaded_at": doc["uploaded_at"]
            })

        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        import traceback
        error_details = str(e) + " | " + traceback.format_exc()
        print(f"List documents error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {error_details}")
