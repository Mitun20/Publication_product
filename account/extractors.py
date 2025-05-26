from docx import Document
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
from docx import Document
from docx.oxml.ns import qn
import re
from docx.text.paragraph import Paragraph
from docx.table import Table

def sanitize_filename(text):
    match = re.match(r'fig\s*\d*\s*:\s*(.+)', text, re.I)
    if match:
        caption_text = match.group(1)
    else:
        caption_text = text

    caption_text = caption_text.lower().strip()
    caption_text = re.sub(r'[^\w\-_. ]', '', caption_text)
    caption_text = caption_text.replace(' ', '_')

    return caption_text if caption_text else 'image'


def extract_docx(filepath):
    doc = Document(filepath)
    text = []

    media_dir = "extracted_images"
    os.makedirs(media_dir, exist_ok=True)

    pending_image = None
    pending_image_ext = None

    for block in iter_block_items(doc):
        if 'paragraph' in block:
            para = block['paragraph'].strip()
            if pending_image and re.match(r'fig\s*\d*\s*:', para, re.I):
                filename_base = sanitize_filename(para)
                image_filename = f"{filename_base}.{pending_image_ext}"
                image_path = os.path.join(media_dir, image_filename)
                with open(image_path, 'wb') as f:
                    f.write(pending_image.blob)
                text.append(para)
                text.append(f"<<IMAGE:{image_path}>>")
                pending_image = None
                pending_image_ext = None
            else:
                if para:
                    text.append(para)

        elif 'image' in block:
            pending_image = block['image']
            pending_image_ext = pending_image.content_type.split('/')[-1]

        elif 'table' in block:
            table_data = block['table']
            for row in table_data:
                text.append('\t'.join(row))

    if pending_image:
        default_name = f"image_{len(text)}.{pending_image_ext}"
        image_path = os.path.join(media_dir, default_name)
        with open(image_path, 'wb') as f:
            f.write(pending_image.blob)
        text.append(f"<<IMAGE:{image_path}>>")

    return '\n'.join(text)


def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag == qn('w:tbl'):
            table = Table(child, parent)
            data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                data.append(row_data)
            yield {'table': data}

        elif child.tag == qn('w:p'):
            paragraph = Paragraph(child, parent)
            if paragraph.text.strip():
                yield {'paragraph': paragraph.text.strip()}
            for run in paragraph.runs:
                if 'graphic' in run._element.xml:
                    drawing = run._element.xpath('.//pic:pic')
                    if drawing:
                        blip = drawing[0].xpath('.//a:blip')[0]
                        embed = blip.get(qn('r:embed'))
                        image_part = parent.part.related_parts[embed]
                        yield {'image': image_part}

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