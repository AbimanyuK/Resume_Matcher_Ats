import os
from typing import Optional
import fitz  
import pdfplumber
from docx import Document
from pdf2image import convert_from_path
import pytesseract

def extract_text_from_txt(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_pdf_text(path: str) -> str:
    full_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return '\n'.join(full_text)

def extract_text_from_pdf_ocr(path: str) -> str:
    pages = convert_from_path(path, dpi=300)
    text = []
    for page in pages:
        text.append(pytesseract.image_to_string(page))
    return '\n'.join(text)

def is_pdf_scanned(path: str, threshold: float = 0.1) -> bool:
    text = extract_text_from_pdf_text(path)
    doc = fitz.open(path)
    avg_chars_per_page = 1000  
    if len(text) < avg_chars_per_page * len(doc) * threshold:
        return True
    return False

def extract_text_from_file(path: str) -> Optional[str]:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.pdf':
            if is_pdf_scanned(path):
                print("Detected scanned PDF, performing OCR...")
                return extract_text_from_pdf_ocr(path)
            else:
                print("Detected text PDF, extracting text directly...")
                return extract_text_from_pdf_text(path)
        elif ext == '.docx':
            return extract_text_from_docx(path)
        elif ext == '.txt':
            return extract_text_from_txt(path)
        else:
            print(f"Unsupported file extension: {ext}")
            return None
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return None