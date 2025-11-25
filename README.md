# AI-Powered Document Intake & Extraction Microservice

## Overview
This is an AI-powered microservice built with FastAPI that extracts and parses student and exam-related information from PDFs and images. The service uses OCR technology to extract text and then applies regex patterns to identify and extract key fields.

## Features
- Async processing with FastAPI
- OCR text extraction using pytesseract
- Regex-based parsing for exam-related fields
- MongoDB storage for processed documents
- RESTful API endpoints

## Key Extracted Fields
- Student Name
- Question Numbers and Questions
- Marks Allocation
- Subject Information
- Class/Section
- Exam Date and Duration
- Question Types

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Tesseract OCR on your system:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

## Environment Configuration
Create a `.env` file in the root directory:
```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>
MONGODB_DB=ocr
MONGODB_COLLECTION=ocr_assignment
```

## Usage

### Start the Server
```bash
cd app
uvicorn main:app --reload
```

### API Endpoints

#### Upload a Document
- **POST** `/upload`
- Upload a PDF, PNG, or JPG file containing exam or student information
- Returns a document ID for later retrieval

#### Retrieve Processed Data
- **GET** `/results/{doc_id}`
- Fetch previously processed document data using the document ID
- Returns extracted fields and original text

#### Service Information
- **GET** `/`
- Returns basic service information and available endpoints

## Example Usage

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf"
```

### Retrieve Processed Data
```bash
curl -X GET "http://localhost:8000/results/{doc_id}" \
  -H "accept: application/json"
```

## Response Format
The response includes:
- Document ID
- Original filename
- Upload timestamp
- Processed pages with extracted text
- Parsed fields including names, questions, marks, etc.

## Technologies Used
- FastAPI (web framework)
- Pytesseract (OCR)
- MongoDB (data storage)
- Regex (text parsing)
- PDF2Image (PDF handling)

## Error Handling
- Invalid file types return 400 Bad Request
- Missing documents return 404 Not Found
- Database errors are logged and handled gracefully
- OCR processing errors return 500 Internal Server Error

## Development Notes
This service is designed specifically for processing exam papers and student-related documents. The regex patterns are optimized for common exam paper formats and should extract the most relevant information including student details, questions, and marks allocation.