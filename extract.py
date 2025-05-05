from docx import Document

def extract_text_from_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

if __name__ == "__main__":
    text = extract_text_from_docx("Editorial Manager.docx")
    
    with open("document_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print("✅ Text extracted and saved to document_text.txt")