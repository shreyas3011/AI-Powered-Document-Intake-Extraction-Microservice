# app/parsers.py
import re
from typing import Dict, List, Optional

# Enhanced regex patterns for exam-style PDFs / student sheets
# These are specifically designed to extract student and exam related fields

# 1) Name: look for variations like "Name:", "Student Name", "Roll No:", "Enrollment:", etc.
NAME_PATTERNS = [
    re.compile(r"(?:Name|Student Name|Candidate Name)[:\s\-\.]{1,5}([A-Z][A-Za-z\s\.\-]{2,60})(?=\s*$|(?<!\w)\d{1,3}(?:\.|\s|$))", re.IGNORECASE),
    re.compile(r"(?:Roll No|Roll Number|Enrollment No)[:\s\-\.]{1,5}([A-Z0-9][A-Za-z0-9\s\.\-]{1,30})", re.IGNORECASE),
    re.compile(r"(?:Student ID|Reg No)[:\s\-\.]{1,5}([A-Z0-9][A-Za-z0-9\s\.\-]{1,30})", re.IGNORECASE),
]

# 2) Question number and question: handle various formats like "1. Question text", "Q1: Question", etc.
QUESTION_PATTERN = re.compile(r"(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*|#\s*)?(\d{1,3})[\.\:\)\-\s]\s*(.+?)(?=\n\s*(?:Q(?:uestion)?\.?\s*\d+|#\s*\d+|\d{1,3}[\.\:\)\-]|\Z))", re.IGNORECASE | re.DOTALL)

# 3) Marks: various formats for marks allocation
MARKS_PATTERNS = [
    re.compile(r"Marks?[:\s\-\.]{1,5}([0-9]{1,3})", re.IGNORECASE),
    re.compile(r"\(([0-9]{1,3})\s*marks?\)", re.IGNORECASE),
    re.compile(r"(\d{1,3})\s*marks?[:\s\-\.]", re.IGNORECASE),
    re.compile(r"Total\s+marks?[:\s\-\.]{1,5}([0-9]{1,3})", re.IGNORECASE),
]

# 4) Subject: identify subject names
SUBJECT_PATTERNS = [
    re.compile(r"(?:Subject|Paper|Course)[:\s\-\.]{1,5}([A-Za-z0-9\s\.\-&/]{2,50})", re.IGNORECASE),
    re.compile(r"(?:^|\n)\s*([A-Z][A-Za-z\s]{5,40})\s+(?:Question Paper|Question|Paper|Exam|Test|Assignment|Midterm|Final)", re.IGNORECASE),
]

# 5) Question types: Multiple Choice, Short Answer, Long Answer, etc.
QUESTION_TYPE_PATTERNS = [
    re.compile(r"(Multiple\s+Choice|MCQ|Short\s+Answer|Long\s+Answer|Essay|True/False|Fill\s+in\s+the\s+Blanks)", re.IGNORECASE),
]

# 6) Additional student information
STUDENT_INFO_PATTERNS = {
    "class": re.compile(r"(?:Class|Grade|Standard)[:\s\-\.]{1,5}([A-Za-z0-9\s\.\-]{1,30})", re.IGNORECASE),
    "section": re.compile(r"(?:Section|Div)[:\s\-\.]{1,5}([A-Za-z0-9\s\.\-]{1,10})", re.IGNORECASE),
    "exam_date": re.compile(r"(?:Date|Exam Date)[:\s\-\.]{1,5}([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4})", re.IGNORECASE),
    "exam_duration": re.compile(r"(?:Duration|Time)[:\s\-\.]{1,5}([0-9]{1,2}\s*hours?|[0-9]{1,2}:[0-9]{2}|[0-9]{1,2}\s*h\s*[0-9]{1,2}\s*m)", re.IGNORECASE),
}

def find_name(text: str) -> Optional[str]:
    for pat in NAME_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None

def find_marks(text: str) -> Optional[str]:
    for pat in MARKS_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None

def find_subject(text: str) -> Optional[str]:
    for pat in SUBJECT_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None

def find_questions(text: str) -> List[Dict]:
    results = []

  
    # Pattern: Q1. Question text (10 marks) or 1. Question text (marks)
    pattern_with_marks = re.compile(r"(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?(\d{1,3})[\.\:\)\-\s]\s*(.+?)\s*\(([0-9]+)\s*marks?\)", re.IGNORECASE | re.DOTALL)
    for m in pattern_with_marks.finditer(text):
        qnum = m.group(1).strip()
        qtext = m.group(2).strip()
        qtext = re.sub(r"\s+", " ", qtext)
        results.append({"question_number": qnum, "question": qtext})

    # Method 2: Look for questions followed by next question or end of text
    if not results:
        for m in QUESTION_PATTERN.finditer(text):
            qnum = m.group(1).strip()
            qtext = m.group(2).strip()
            
            qtext = re.sub(r"\s+", " ", qtext)
            
            qtext = re.split(r'\([0-9]+\s*marks?\)', qtext)[0].strip()
            
            if len(qtext) > 10:  
                results.append({"question_number": qnum, "question": qtext})

    # Method 3: Try simpler pattern if no questions found yet
    if not results:
        simple_pattern = re.compile(r"(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?(\d{1,3})[\.\:\)\-\s]\s*([^\n]+)", re.IGNORECASE)
        for m in simple_pattern.finditer(text):
            qnum = m.group(1).strip()
            qtext = m.group(2).strip()
            qtext = re.sub(r"\s+", " ", qtext)
            if len(qtext) > 5:
                results.append({"question_number": qnum, "question": qtext})

   
    unique_questions = []
    seen_questions = set()
    for q in results:
        
        norm_text = re.sub(r'\s+', ' ', q['question']).lower()
        if norm_text not in seen_questions:
            seen_questions.add(norm_text)
            unique_questions.append(q)

    return unique_questions

def find_question_types(text: str) -> List[str]:
    results = []
    for pattern in QUESTION_TYPE_PATTERNS:
        matches = pattern.findall(text)
        results.extend(matches)
    return list(set(results))  

def find_student_info(text: str) -> Dict[str, Optional[str]]:
    info = {}
    for key, pattern in STUDENT_INFO_PATTERNS.items():
        match = pattern.search(text)
        info[key] = match.group(1).strip() if match else None
    return info

def parse_page(text: str) -> Dict:
    # Extract all fields
    name = find_name(text)
    marks = find_marks(text)
    subject = find_subject(text)
    questions = find_questions(text)
    question_types = find_question_types(text)
    student_info = find_student_info(text)

    
    result = {
        "name": name,
        "subject": subject,
        "marks": marks,
        "questions": questions,
        "question_types": question_types,
        "class": student_info.get("class"),
        "section": student_info.get("section"),
        "exam_date": student_info.get("exam_date"),
        "exam_duration": student_info.get("exam_duration")
    }

    
    return {k: v for k, v in result.items() if v is not None and v != []}
