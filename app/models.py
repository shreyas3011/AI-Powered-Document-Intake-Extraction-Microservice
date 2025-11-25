# app/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

class Question(BaseModel):
    question_number: str
    question: str

class ParsedField(BaseModel):
    field_name: str
    value: Optional[str]

class PageResult(BaseModel):
    page_number: int
    text: str
    parsed: List[ParsedField] = []
    extracted_data: Optional[Dict[str, Any]] = None

class DocumentRecord(BaseModel):
    id: Optional[str] = None
    filename: str
    uploaded_at: datetime
    pages: List[PageResult]
    raw_text: Optional[str] = None
    parsing_errors: Optional[List[str]] = []
