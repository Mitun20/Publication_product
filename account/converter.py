import re
from typing import Dict, List, Tuple, Optional

class LatexConverter:
    def __init__(self):
        self.figure_count = 1
        self.table_count = 1
        self.current_list_type = None
        self.list_stack = []
        self.section_depth = 0

    def convert_to_latex(self, text: str) -> str:
        text = self._normalize_line_endings(text)
        metadata, body = self._extract_metadata(text)
        processed_body = self._process_body(body)
        return self._generate_latex_document(metadata, processed_body)

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace('\r\n', '\n').replace('\r', '\n')

    def _extract_metadata(self, text: str) -> Tuple[Dict[str, str], str]:
        lines = text.split('\n')
        metadata = {
            'title': '',
            'authors': [],
            'abstract': '',
            'keywords': '',
            'acknowledgments': '',
            'date': r'\today'
        }
        body_lines = []
        current_section = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and stripped:
                metadata['title'] = stripped
                continue
            if not current_section:
                if stripped.lower().startswith('abstract'):
                    current_section = 'abstract'
                    metadata['abstract'] = stripped.split(':', 1)[-1].strip() if ':' in stripped else ''
                    continue
                elif any(stripped.lower().startswith(kw) for kw in ['key terms', 'keywords']):
                    current_section = 'keywords'
                    metadata['keywords'] = stripped.split(':', 1)[-1].strip() if ':' in stripped else ''
                    continue
                elif any(stripped.lower().startswith(ack) for ack in ['acknowledgment', 'acknowledgement']):
                    current_section = 'acknowledgments'
                    metadata['acknowledgments'] = stripped.split(':', 1)[-1].strip() if ':' in stripped else ''
                    continue
                elif ('@' in stripped or any(term in stripped.lower() for term in 
                    ['professor', 'department', 'university', 'college', 'institute'])):
                    metadata['authors'].append(stripped)
                    continue
            if current_section:
                if not stripped or stripped.lower().startswith(('introduction', 'section', '\d+\.')):
                    current_section = None
                    if stripped: 
                        body_lines.append(line)
                else:
                    metadata[current_section] += ' ' + stripped
                continue
            body_lines.append(line)
        for key in ['title', 'abstract', 'keywords', 'acknowledgments']:
            metadata[key] = ' '.join(metadata[key].split())
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)
        return metadata, '\n'.join(body_lines)

    def _process_body(self, body: str) -> str:
        # Apply all processors to the whole body, not per paragraph
        body = self._process_sections(body)
        body = self._process_lists(body)
        body = self._process_tables(body)
        body = self._process_figures_with_captions(body)
        body = self._process_equations(body)
        body = self._process_citations(body)
        body = self._process_alignments(body)
        body = self._process_formatting(body)
        body = self._process_references(body)
        return body

    def _escape_latex_text(self, text: str) -> str:
        # Escape only in plain text, not in LaTeX commands
        special_chars = {
            '%': r'\%',
            '$': r'\$',
            '&': r'\&',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
            '–': '--',
            '—': '---',
            '“': '``',
            '”': "''",
            '‘': '`',
            '’': "'"
        }
        for char, escape in special_chars.items():
            text = text.replace(char, escape)
        return text

    def _process_paragraph(self, text: str) -> str:
        # Order: formatting, lists, tables, figures, equations, citations, alignments, sections
        text = self._process_formatting(text)
        text = self._process_lists(text)
        text = self._process_tables(text)
        text = self._process_figures_with_captions(text)
        text = self._process_equations(text)
        text = self._process_citations(text)
        text = self._process_alignments(text)
        text = self._process_sections(text)
        return text

    def _process_sections(self, text: str) -> str:
    # Match lines like "1. Introduction", "2 Introduction", "2.1 Data Collection"
        def section_replacer(match):
            numbers = match.group(1).split('.')
            level = len(numbers)
            title = self._escape_latex_text(match.group(2).strip())
            if level == 1:
                return f'\\section{{{title}}}'
            elif level == 2:
                return f'\\subsection{{{title}}}'
            elif level == 3:
                return f'\\subsubsection{{{title}}}'
            else:
                return f'\\paragraph{{{title}}}'
        # Accept dot or space after the number, and allow lowercase section titles
        text = re.sub(r'(?m)^\s*(\d+(?:\.\d+)*)(?:\.|\s)\s*([A-Za-z][^\n]+)', section_replacer, text)
        return text

    def _process_figures_with_captions(self, text: str) -> str:
        # Convert "Figure X: caption" to LaTeX figure environment (no image, just caption)
        def fig_replacer(match):
            caption = self._escape_latex_text(match.group(1).strip())
            label = f"fig{self.figure_count}"
            self.figure_count += 1
            return (
                f'\\begin{{figure}}[htbp]\n'
                f'\\centering\n'
                f'\\caption{{{caption}}}\n'
                f'\\label{{{label}}}\n'
                f'\\end{{figure}}'
            )
        # Handles both markdown images and plain Figure captions
        text = re.sub(r'Figure\s*\d+:\s*([^\n]+)', fig_replacer, text)
        return text

    def _process_tables(self, text: str) -> str:
        def table_block_replacer(match):
            block = match.group(0)
            lines = [l for l in block.strip().split('\n') if l.strip()]
            if len(lines) < 2:
                return block
            headers = re.split(r'\s{2,}|\t+', lines[0])
            aligns = ['l'] * len(headers)
            latex = [
                '\\begin{table}[htbp]',
                '\\centering',
                '\\begin{tabular}{%s}' % ('|'.join(aligns)),
                '\\toprule',
                ' & '.join(self._escape_latex_text(h.strip()) for h in headers) + r' \\',
                '\\midrule'
            ]
            for row in lines[1:]:
                cells = re.split(r'\s{2,}|\t+', row)
                latex.append(' & '.join(self._escape_latex_text(c.strip()) for c in cells) + r' \\')
            latex.extend([
                '\\bottomrule',
                '\\end{tabular}',
                '\\end{table}'
            ])
            return '\n'.join(latex)
        # Find blocks of 2+ lines with 2+ spaces or tabs
        return re.sub(r'((?:[^\n]*\s{2,}[^\n]*\n){1,}[^\n]*\s{2,}[^\n]*\n?)|((?:[^\n]*\t+[^\n]*\n){1,}[^\n]*\t+[^\n]*\n?)', table_block_replacer, text)

    def _process_equations(self, text: str) -> str:
        # Block equations: $$...$$ or \[...\]
        text = re.sub(
            r'\$\$(.*?)\$\$',
            r'\\begin{equation}\n\1\n\\end{equation}',
            text,
            flags=re.DOTALL
        )
        text = re.sub(
            r'\\\[(.*?)\\\]',
            r'\\begin{align*}\n\1\n\\end{align*}',
            text,
            flags=re.DOTALL
        )
        # Inline equations: $...$
        # Avoid replacing \$ (escaped dollar)
        text = re.sub(r'(?<!\\)\$(.+?)(?<!\\)\$', r'\\(\1\\)', text)
        return text

    def _process_lists(self, text: str) -> str:
        lines = text.split('\n')
        output = []
        in_itemize = False
        in_enumerate = False
        for line in lines:
            stripped = line.strip()
            # Bullet list (•, -, *, +) anywhere after optional whitespace
            if re.match(r'^(?:\s*)(•|-|\*|\+)\s+', line):
                if not in_itemize:
                    output.append(r'\begin{itemize}')
                    in_itemize = True
                content = re.sub(r'^(?:\s*)(•|-|\*|\+)\s*', '', line)
                output.append(r'\item ' + content)
            # Numbered list (1., 2., etc.) at start of line or after whitespace
            elif re.match(r'^(?:\s*)\d+\.\s+', line):
                if not in_enumerate:
                    output.append(r'\begin{enumerate}')
                    in_enumerate = True
                content = re.sub(r'^(?:\s*)\d+\.\s*', '', line)
                output.append(r'\item ' + content)
            else:
                if in_itemize:
                    output.append(r'\end{itemize}')
                    in_itemize = False
                if in_enumerate:
                    output.append(r'\end{enumerate}')
                    in_enumerate = False
                output.append(line)
        if in_itemize:
            output.append(r'\end{itemize}')
        if in_enumerate:
            output.append(r'\end{enumerate}')
        return '\n'.join(output)

    def _process_citations(self, text: str) -> str:
        # [1] or [1,2,3]
        text = re.sub(r'\[(\d+(?:,\s*\d+)*)\]', lambda m: '\\cite{' + m.group(1).replace(' ', '') + '}', text)
        return text

    def _process_formatting(self, text: str) -> str:
        # Bold+italic (***text***)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)
        # Bold (**text**)
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
        # Italic (*text*)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\\textit{\1}', text)
        # Underline (__text__)
        text = re.sub(r'__(.+?)__', r'\\underline{\1}', text)
        return text

    def _process_alignments(self, text: str) -> str:
        # Center: ::center ... ::endcenter
        text = re.sub(
            r'::center\s*\n(.*?)\n::endcenter',
            lambda m: '\\begin{center}\n' + m.group(1).strip() + '\n\\end{center}',
            text, flags=re.DOTALL
        )
        # Right: ::right ... ::endright
        text = re.sub(
            r'::right\s*\n(.*?)\n::endright',
            lambda m: '\\begin{flushright}\n' + m.group(1).strip() + '\n\\end{flushright}',
            text, flags=re.DOTALL
        )
        # Left: ::left ... ::endleft
        text = re.sub(
            r'::left\s*\n(.*?)\n::endleft',
            lambda m: '\\begin{flushleft}\n' + m.group(1).strip() + '\n\\end{flushleft}',
            text, flags=re.DOTALL
        )
        return text

    def _process_references(self, text: str) -> str:
        # Convert references at the end to LaTeX thebibliography
        if 'References' in text:
            parts = text.split('References', 1)
            main = parts[0]
            refs = parts[1].strip().split('\n')
            bib = ['\\section*{References}', '\\begin{thebibliography}{99}']
            for ref in refs:
                m = re.match(r'(\d+)\.\s*(.+)', ref)
                if m:
                    bib.append(f'\\bibitem{{ref{m.group(1)}}} {self._escape_latex_text(m.group(2))}')
            bib.append('\\end{thebibliography}')
            return main + '\n' + '\n'.join(bib)
        return text

    def _escape_latex(self, text: str) -> str:
        # Protect LaTeX commands
        protected = []
        pos = 0
        for match in re.finditer(r'\\(?:[a-zA-Z]+|.)', text):
            protected.append(text[pos:match.start()])
            protected.append(f'\\LATEXPROTECTED{{{match.group(0)}}}')
            pos = match.end()
        protected.append(text[pos:])
        text = ''.join(protected)
        special_chars = {
            '%': r'\%',
            '$': r'\$',
            '&': r'\&',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}',
            '–': '--',
            '—': '---',
            '“': '``',
            '”': "''",
            '‘': '`',
            '’': "'"
        }
        for char, escape in special_chars.items():
            text = text.replace(char, escape)
        # Restore protected LaTeX commands
        text = text.replace(r'\LATEXPROTECTED{', '')
        text = text.replace('}', '')
        return text

    def _generate_latex_document(self, metadata: Dict[str, str], body: str) -> str:
        authors = ' \\\\ '.join(metadata['authors']) if metadata['authors'] else ''
        latex = f"""\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\usepackage{{babel}}
\\usepackage{{csquotes}}
\\usepackage{{amsmath, amssymb, amsthm}}
\\usepackage{{graphicx}}
\\usepackage{{float}}
\\usepackage{{booktabs}}
\\usepackage{{longtable}}
\\usepackage[colorlinks=true, linkcolor=blue, urlcolor=blue, citecolor=blue]{{hyperref}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage{{geometry}}
\\usepackage{{fancyhdr}}
\\usepackage{{tikz}}
\\usepackage{{pgfplots}}
\\usepackage{{biblatex}}

\\geometry{{a4paper, margin=1in}}
\\pagestyle{{plain}}
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{1em}}
\\setlist[itemize]{{leftmargin=*,nosep}}
\\setlist[enumerate]{{leftmargin=*}}

\\title{{{metadata['title']}}}
\\author{{{authors}}}
\\date{{{metadata['date']}}}

\\begin{{document}}

\\maketitle
"""
        if metadata['abstract']:
            latex += f"""
\\begin{{abstract}}
{metadata['abstract']}
\\end{{abstract}}
"""
        if metadata['keywords']:
            latex += f"""
\\providecommand{{\\keywords}}[1]{{\\textbf{{Keywords:}} #1}}
\\keywords{{{metadata['keywords']}}}
"""
        latex += """
\\tableofcontents
"""
        latex += body
        if metadata['acknowledgments']:
            latex += f"""
\\section*{{Acknowledgments}}
{metadata['acknowledgments']}
"""
        latex += """
\\printbibliography

\\end{document}
"""
        return latex

def text_to_latex(text: str, doc_type: str = 'article', **kwargs) -> str:
    converter = LatexConverter()
    return converter.convert_to_latex(text)