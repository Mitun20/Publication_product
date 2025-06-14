import re

def escape_latex(text):
    replace_map = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    regex = re.compile('|'.join(re.escape(key) for key in replace_map.keys()))
    return regex.sub(lambda match: replace_map[match.group()], text)

def convert_text_to_ieee_latex(input_text):
    lines = input_text.splitlines()
    n = len(lines)
    i = 0
    latex = []

    # Preamble
    latex.append(r"\documentclass[conference]{IEEEtran}")
    latex.append(r"\IEEEoverridecommandlockouts")
    latex.append(r"\usepackage{cite,amsmath,amssymb,amsfonts,algorithmic,graphicx,textcomp,xcolor}")
    latex.append(r"\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em"
                 r"T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}")
    latex.append("")

    # Title (first line)
    title = lines[i].strip()
    latex.append(r"\title{" + escape_latex(title) + "}")
    i += 1

    # Parse authors block until first section or empty line after authors
    author_lines = []
    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if re.match(r"^\d+\.", line) or line.lower() in ["introduction", "applications", "conclusion", "contact"]:
            break
        author_lines.append(line)
        i += 1

    # Break authors on email lines
    author_blocks = []
    block = []
    for line in author_lines:
        block.append(line)
        if "@" in line:
            author_blocks.append(block)
            block = []
    if block:
        author_blocks.append(block)

    def parse_author_block(block):
        # The first line contains full name and role
        roles = ["Associate Professor", "Assistant Professor", "Professor"]
        line = block[0]

        role_found = ""
        name = line
        for r in roles:
            if r in line:
                role_found = r
                idx = line.find(r)
                name = line[:idx].strip()
                break

        email = ""
        dept_inst = []
        for l in block[1:]:
            if "@" in l:
                email = l.strip()
            else:
                dept_inst.append(l.strip())

        department = ""
        institution = ""
        if dept_inst:
            department = dept_inst[0]
            if len(dept_inst) > 1:
                institution = " ".join(dept_inst[1:])

        return {
            "name": name,
            "role": role_found,
            "department": department,
            "institution": institution,
            "email": email,
        }

    authors = [parse_author_block(b) for b in author_blocks]

    latex.append(r"\author{")
    for idx, a in enumerate(authors):
        name_line = escape_latex(a["name"])
        if a["role"]:
            name_line += " " + escape_latex(a["role"])
        latex.append(r"\IEEEauthorblockN{" + name_line + "}")
        affil = []
        if a["department"]:
            affil.append(escape_latex(a["department"]))
        if a["institution"]:
            affil.append(escape_latex(a["institution"]))
        affil_str = r"\\ ".join(affil)
        latex.append(r"\IEEEauthorblockA{" + affil_str + r"\\" + f"Email: \\texttt{{{escape_latex(a['email'])}}}" + "}")
        if idx != len(authors) - 1:
            latex.append(r"\and")
    latex.append(r"}")
    latex.append("")

    latex.append(r"\begin{document}")
    latex.append(r"\maketitle")
    latex.append("")

    def is_table_line(line):
        return line.strip().startswith("|") and line.strip().endswith("|")

    def process_table(start_idx):
        table_lines = []
        idx = start_idx
        while idx < n and is_table_line(lines[idx]):
            table_lines.append(lines[idx].strip())
            idx += 1
        headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
        data_rows = []
        for l in table_lines[2:]:
            row = [c.strip() for c in l.strip("|").split("|")]
            data_rows.append(row)

        captions = []
        cap_idx = idx
        while cap_idx < n and lines[cap_idx].strip() != "":
            cap_line = lines[cap_idx].strip()
            if cap_line.lower().startswith("table:"):
                captions.append(cap_line[6:].strip())
            else:
                break
            cap_idx += 1
        return headers, data_rows, captions, cap_idx

    def prettify_caption(caption):
        caption = caption.strip()
        if not caption:
            return ""
        return caption[0].upper() + caption[1:].replace("_", " ")

    def unescape_graphics_path(path):
        return path.replace("\\", "/")

    while i < n:
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Numbered sections
        m_sec = re.match(r"^(\d+)\.\s+(.*)", line)
        if m_sec:
            sec_title = m_sec.group(2)
            latex.append(r"\section{" + escape_latex(sec_title) + "}")
            i += 1
            continue

        # Section keywords without number
        if line.lower() in ["introduction", "applications", "conclusion", "contact"]:
            if line.lower() == "contact":
                latex.append(r"\section*{Contact}")
                i += 1
                contact_lines = []
                while i < n and lines[i].strip():
                    contact_lines.append(lines[i].strip())
                    i += 1
                contact_text = " ".join(contact_lines)
                m_email = re.search(r"Email:\s*(\S+)", contact_text)
                if m_email:
                    email = m_email.group(1)
                    contact_text = contact_text.replace(m_email.group(0), "")
                    latex.append(r"Contact: " + escape_latex(contact_text.strip()))
                    latex.append(r"\\")
                    latex.append(r"Email: \texttt{" + escape_latex(email) + "}")
                else:
                    latex.append(escape_latex(contact_text))
                continue
            else:
                latex.append(r"\section{" + escape_latex(line) + "}")
                i += 1
                continue

        # Bullet lists
        if re.match(r"^(\*|•|-)\s+", line):
            latex.append(r"\begin{itemize}")
            while i < n and re.match(r"^(\*|•|-)\s+", lines[i].strip()):
                item = re.sub(r"^(\*|•|-)\s+", "", lines[i].strip())
                latex.append(r"\item " + escape_latex(item))
                i += 1
            latex.append(r"\end{itemize}")
            continue

        # Tables
        if is_table_line(line):
            headers, data_rows, captions, new_i = process_table(i)
            latex.append(r"\begin{table}[h]")
            latex.append(r"\centering")
            col_fmt = "|" + "c|" * len(headers)
            latex.append(r"\begin{tabular}{" + col_fmt + "}")
            latex.append(r"\hline")
            latex.append(" & ".join(escape_latex(h) for h in headers) + r" \\")
            latex.append(r"\hline")
            for row in data_rows:
                latex.append(" & ".join(escape_latex(cell) for cell in row) + r" \\")
            latex.append(r"\hline")
            latex.append(r"\end{tabular}")
            if captions:
                unique_captions = ", ".join(sorted(set(captions)))
                latex.append(r"\caption{" + escape_latex(prettify_caption(unique_captions)) + "}")
            latex.append(r"\end{table}")
            i = new_i
            # Skip any remaining "Table: ..." lines
            while i < n and lines[i].strip().lower().startswith("table:"):
                i += 1
            continue

        # Figures placeholders
        m_figtext = re.match(r"Fig\s*\d*\s*:\s*(.+)", line, re.I)
        if m_figtext:
            cap_text = m_figtext.group(1).strip()
            latex.append("% Figure placeholder for: " + escape_latex(cap_text))
            i += 1
            continue

        m_img = re.match(r"<<IMAGE:(.+)>>", line)
        if m_img:
            img_path = m_img.group(1).strip()
            base_name = img_path.split("/")[-1]
            cap_text = base_name.rsplit(".", 1)[0].replace("_", " ").title()
            label_text = re.sub(r"[^a-zA-Z0-9]+", "", base_name)
            latex.append(r"\begin{figure}[h]")
            latex.append(r"\centering")
            latex.append(r"\includegraphics[width=0.6\linewidth]{" + unescape_graphics_path(img_path) + "}")
            latex.append(r"\caption{" + escape_latex(cap_text) + "}")
            latex.append(r"\label{fig:" + label_text + "}")
            latex.append(r"\end{figure}")
            i += 1
            continue

        # Paragraphs
        para_lines = []
        while i < n and lines[i].strip() and not is_table_line(lines[i]) and not re.match(r"Fig\s*\d*\s*:", lines[i], re.I) and not re.match(r"<<IMAGE:.+>>", lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        if para_lines:
            paragraph = " ".join(para_lines)
            latex.append(escape_latex(paragraph))
            latex.append("")
            continue

        i += 1

    latex.append(r"\end{document}")
    return "\n".join(latex)

def text_to_latex(markdown_text: str) -> str:
    return convert_text_to_ieee_latex(markdown_text)
