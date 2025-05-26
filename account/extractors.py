from docx import Document
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
from docx import Document
from docx.oxml.ns import qn
import re


def sanitize_filename(text):
    # Clean figure caption to make it safe for filenames
    text = text.lower().strip()
    text = re.sub(r'fig:\s*', '', text)  # Remove "Fig:"
    text = re.sub(r'[^\w\-_. ]', '', text)  # Remove unsafe chars
    text = text.replace(' ', '_')
    return text

def extract_docx(filepath):
    doc = Document(filepath)
    text = []

    media_dir = "extracted_images"
    os.makedirs(media_dir, exist_ok=True)

    pending_fig_label = None

    for block in iter_block_items(doc):
        if isinstance(block, str):
            if block.strip().lower().startswith("fig:"):
                pending_fig_label = block.strip()
            else:
                text.append(block)
        elif isinstance(block, list):
            text.append('\t'.join(block))
        elif isinstance(block, dict) and 'image' in block:
            image = block['image']
            ext = image.content_type.split("/")[-1]

            # Use figure label to name image, or fallback
            if pending_fig_label:
                filename_base = sanitize_filename(pending_fig_label)
                text.append(pending_fig_label)
                pending_fig_label = None
            else:
                filename_base = f"image_{len(text)}"

            image_filename = f"{filename_base}.{ext}"
            image_path = os.path.join(media_dir, image_filename)

            with open(image_path, 'wb') as f:
                f.write(image.blob)

            text.append(f"<<IMAGE:{image_path}>>")

    return '\n'.join(text)

def iter_block_items(parent):
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    for child in parent.element.body.iterchildren():
        if child.tag == qn('w:p'):
            paragraph = Paragraph(child, parent)
            para_text = paragraph.text.strip()
            if para_text:
                yield para_text

            for run in paragraph.runs:
                if 'graphic' in run._element.xml:
                    drawing = run._element.xpath('.//pic:pic')
                    if drawing:
                        blip = drawing[0].xpath('.//a:blip')[0]
                        embed = blip.get(qn('r:embed'))
                        image_part = parent.part.related_parts[embed]
                        yield {'image': image_part}

        elif child.tag == qn('w:tbl'):
            table = Table(child, parent)
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                if any(row_data):
                    yield row_data


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