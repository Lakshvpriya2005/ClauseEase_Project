import os
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_file(filepath):
    """Extract text from PDF or DOCX files"""
    _, ext = os.path.splitext(filepath.lower())
    
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext == '.docx':
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text.strip()

def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = Document(filepath)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")
    
    return text.strip()
