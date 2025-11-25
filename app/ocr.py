# app/ocr.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import asyncio
from typing import List, Tuple



async def image_to_text_async(image_path: str) -> str:
    
    def ocr_with_error_handling():
        try:
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as e:
            print(f"OCR error on {image_path}: {e}")
            return ""  

    return await asyncio.to_thread(ocr_with_error_handling)

async def pdf_to_images(pdf_path: str, dpi: int = 300) -> List[str]:
   
    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, img in enumerate(images):
        tmp_path = f"{pdf_path}_page_{i+1}.png"
        img.save(tmp_path, "PNG")
        image_paths.append(tmp_path)
    return image_paths

async def extract_text_from_file(path: str) -> Tuple[List[str], List[int]]:
    """
    Return (list_of_text_per_page, list_of_page_numbers)
    For images: one page
    For PDFs: multiple pages
    Clean up temporary image files after OCR.
    """
    lower = path.lower()
    image_paths = []
    try:
        if lower.endswith(".pdf"):
            image_paths = await pdf_to_images(path)
        else:
            image_paths = [path]
        
        tasks = [image_to_text_async(p) for p in image_paths]
        pages_text = await asyncio.gather(*tasks)
        page_numbers = list(range(1, len(pages_text) + 1))
        return pages_text, page_numbers
    finally:
        
        for p in image_paths:
            if p != path and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
