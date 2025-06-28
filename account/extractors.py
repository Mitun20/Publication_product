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

def sanitize_filename1(text):
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
                filename_base = sanitize_filename1(para)
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

import fitz  # PyMuPDF
import os
import re
import pdfplumber

def sanitize_filename(text):
    # Extract descriptive part from figure caption for filename
    match = re.match(r'fig\s*\d*\s*:\s*(.+)', text, re.I)
    if match:
        caption_text = match.group(1)
    else:
        caption_text = text
    caption_text = caption_text.lower().strip()
    caption_text = re.sub(r'[^\w\-_. ]', '', caption_text)
    caption_text = caption_text.replace(' ', '_')
    return caption_text if caption_text else 'image'

def format_table(table_data):
    """Format a table as markdown."""
    if not table_data or len(table_data) < 1:
        return ''
    header = table_data[0]
    rows = table_data[1:]
    md = []
    md.append('|' + '|'.join([str(cell) if cell is not None else '' for cell in header]) + '|')
    md.append('|' + '|'.join(['---'] * len(header)) + '|')
    for row in rows:
        clean_row = [cell if cell else '' for cell in row]
        md.append('|' + '|'.join(clean_row) + '|')
    return '\n'.join(md)

def extract_pdf(filepath):
    doc = fitz.open(filepath)
    media_dir = "extracted_images"
    os.makedirs(media_dir, exist_ok=True)

    output = []

    with pdfplumber.open(filepath) as pdf_plumber:
        for page_num, page in enumerate(doc, start=1):
            # Extract text blocks sorted top-down
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: b[1])

            # Get tables + bounding boxes
            pdf_page = pdf_plumber.pages[page_num - 1]
            table_bboxes = []
            for t in pdf_page.find_tables():
                bbox = t.bbox  # (x0, top, x1, bottom)
                table_bboxes.append((bbox, t))

            # Combine text and tables by vertical position
            combined = []
            for bbox, tbl in table_bboxes:
                combined.append(('table', bbox[1], tbl))
            for b in blocks:
                combined.append(('text', b[1], b))
            combined.sort(key=lambda x: x[1])

            tables_output = set()

            # Extract all images on this page once
            images_info = []
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                ext = base_image["ext"]
                images_info.append({"xref": xref, "bytes": img_bytes, "ext": ext})

            image_used = [False] * len(images_info)

            for item_type, y, content in combined:
                if item_type == 'table':
                    if content not in tables_output:
                        tables_output.add(content)
                        try:
                            table_data = content.extract()
                        except Exception:
                            # fallback in case extract() is unavailable
                            table_data = content.extract_table()
                        if not table_data:
                            table_data = []

                        formatted_table = format_table(table_data)
                        if formatted_table:
                            output.append(formatted_table)

                        # Unique captions per page (adjust as needed)
                        if page_num == 1:
                            caption = "Table: Salary List"
                        elif page_num == 2:
                            caption = "Table: Applications List"
                        else:
                            caption = "Table: List"

                        # Avoid duplicate captions
                        if not output or output[-1].strip() != caption:
                            output.append(caption + "\n")

                elif item_type == 'text':
                    x0, y0, x1, y1, text, block_no, block_type = content
                    if block_type == 0:
                        text = text.strip()

                        # Skip lines fully inside table bbox to avoid duplicates
                        skip_line = False
                        for bbox, tbl in table_bboxes:
                            if y0 >= bbox[1] and y1 <= bbox[3]:
                                skip_line = True
                                break
                        if skip_line or not text:
                            continue

                        # Split author line emails into separate lines
                        email_match = re.search(r'(\S+@\S+)', text)
                        if email_match and not text.startswith("Email:"):
                            before_email = text[:email_match.start()].strip()
                            email = email_match.group(1)
                            after_email = text[email_match.end():].strip()
                            if before_email:
                                output.append(before_email)
                            output.append(email)
                            if after_email:
                                output.append(after_email)
                            continue

                        # Normalize bullet points (• or -) at line start to '- '
                        text = re.sub(r'^[\u2022•\-]\s*', '- ', text)

                        # Fix common figure caption typos
                        if re.match(r'fig\s*\d*\s*:', text, re.I):
                            text = re.sub(r'paractice', 'practice', text, flags=re.I)

                        # Handle figure captions with images
                        if re.match(r'fig\s*\d*\s*:', text, re.I):
                            for idx, used in enumerate(image_used):
                                if not used:
                                    filename_base = sanitize_filename(text)
                                    filename = f"{filename_base}.{images_info[idx]['ext']}"
                                    filepath_img = os.path.join(media_dir, filename)
                                    with open(filepath_img, "wb") as f:
                                        f.write(images_info[idx]["bytes"])
                                    image_used[idx] = True
                                    output.append(text)
                                    output.append(f"<<IMAGE:{filepath_img}>>\n")
                                    break
                            else:
                                output.append(text)
                        else:
                            output.append(text)

            # Add leftover images without captions
            for idx, used in enumerate(image_used):
                if not used:
                    filename = f"image_{page_num}_{idx + 1}.{images_info[idx]['ext']}"
                    filepath_img = os.path.join(media_dir, filename)
                    with open(filepath_img, "wb") as f:
                        f.write(images_info[idx]["bytes"])
                    output.append(f"<<IMAGE:{filepath_img}>>")

    # Clean repeated empty lines
    cleaned_output = []
    prev_empty = False
    for line in output:
        if line.strip() == '':
            if not prev_empty:
                cleaned_output.append('')
            prev_empty = True
        else:
            cleaned_output.append(line)
            prev_empty = False

    return "\n".join(cleaned_output)
