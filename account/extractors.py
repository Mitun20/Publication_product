from docx import Document
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os

def extract_docx(filepath):
    doc = Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_pdf(filepath):
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join([page.extract_text() for page in reader.pages])

def extract_pdf_ocr(filepath):
    images = convert_from_path(filepath)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    return text