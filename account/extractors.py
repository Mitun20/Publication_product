from docx import Document
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
from docx import Document
import os

def extract_docx(filepath):
    doc = Document(filepath)
    text = []

    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():  # Avoid empty lines
            text.append(para.text.strip())

    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            if any(row_data):  # Avoid empty rows
                text.append('\t'.join(row_data))

    # Extract images
    image_count = 0
    media_dir = "extracted_images"
    os.makedirs(media_dir, exist_ok=True)  # Ensure output folder exists

    for rel in doc.part._rels.values():
        if "image" in rel.reltype:
            image = rel.target_part
            ext = image.content_type.split("/")[-1]
            image_filename = f"image_{image_count}.{ext}"
            image_path = os.path.join(media_dir, image_filename)
            with open(image_path, 'wb') as f:
                f.write(image.blob)
            text.append(f"<<IMAGE:{image_path}>>")
            image_count += 1

    return '\n'.join(text)

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