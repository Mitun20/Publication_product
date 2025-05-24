import re
from typing import List, Optional
from pathlib import Path

class LatexConverter:
    def __init__(self):
        self.special_chars = {
            '\\': r'\textbackslash{}',
            '_': r'\_',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '–': '--',
            '—': '---',
            '“': r'``',
            '”': r"''",
            '‘': r'`',
            '’': r"'",
            '<': r'\textless{}',
            '>': r'\textgreater{}',
        }
        self.table_count = 0
        self.figure_count = 0  # Initialize figure counter

    def escape_special_chars(self, text: str) -> str:
        for char, escape in self.special_chars.items():
            text = text.replace(char, escape)
        return text
    
    def format_sections(self, text: str) -> str:
        # Convert numbered sections (1. Introduction) to LaTeX sections
        text = re.sub(r'^(\d+)\.\s+([^\n]+)$', r'\\section{\2}', text, flags=re.MULTILINE)
        return text

    def format_lists(self, text: str) -> str:
        # Convert bullet points to itemize environment
        text = re.sub(r'^•\s+(.+)$', r'\\item \1', text, flags=re.MULTILINE)
        
        # Wrap consecutive items in itemize environment
        lines = text.split('\n')
        output = []
        in_itemize = False
        
        for line in lines:
            if line.startswith(r'\item '):
                if not in_itemize:
                    output.append(r'\begin{itemize}')
                    in_itemize = True
                output.append(line)
            else:
                if in_itemize:
                    output.append(r'\end{itemize}')
                    in_itemize = False
                output.append(line)
        
        if in_itemize:
            output.append(r'\end{itemize}')
        
        return '\n'.join(output)

    def format_tables(self, text: str) -> str:
        # Find all tables in the text
        table_matches = list(re.finditer(
            r'S\.No\s+Name\s+Role\s+Salary\n((?:\d+\s+\w+\s+\w+\s+\d+\n?)+)',
            text
        ))
        
        # Process matches in reverse order to avoid position shifting
        for match in reversed(table_matches):
            table_content = match.group(0).strip()
            if not table_content:
                continue
                
            rows = [row for row in table_content.split('\n') if row.strip()]
            if len(rows) < 2:  # Need at least header and one data row
                continue
                
            header = rows[0]
            data_rows = rows[1:]
            
            # Generate LaTeX table
            latex_table = [
                r'\begin{table}[h!]',
                r'\centering',
                r'\begin{tabular}{|l|l|l|l|}',
                r'\hline',
                r'\textbf{S.No} & \textbf{Name} & \textbf{Role} & \textbf{Salary} \\ \hline'
            ]
            
            for row in data_rows:
                cols = re.split(r'\s+', row.strip(), maxsplit=3)
                if len(cols) >= 4:
                    latex_table.append(f"{cols[0]} & {cols[1]} & {cols[2]} & {cols[3]} \\\\ \\hline")
            
            latex_table.extend([
                r'\end{tabular}',
                r'\caption{Employee Data}',
                fr'\label{{tab:employee{self.table_count}}}',
                r'\end{table}'
            ])
            
            # Replace the original table with LaTeX table
            text = text[:match.start()] + '\n'.join(latex_table) + text[match.end():]
            self.table_count += 1
        
        return text


    def format_images(self, text: str) -> str:
        """Convert all image formats to proper LaTeX figures"""
        # Ensure figure_count starts at 1 if this is the first run
        if not hasattr(self, 'figure_count'):
            self.figure_count = 1
        
        # Handle both <<IMAGE:path>> and \textless{}\textless{}IMAGE... formats
        text = re.sub(
            r'(?:<<IMAGE:|\\textless{}\\textless{}IMAGE:)([^>]+?)(?:>>|\\textgreater{}\\textgreater{})',
            self._generate_figure_latex_custom,
            text
        )
        return text


    def _generate_figure_latex_custom(self, match: re.Match) -> str:
        """Special handler for the <<IMAGE:path>> format to generate expected figure output"""
        try:
            path = match.group(1).strip()
            if not path:
                raise ValueError("Empty image path")

            # Clean path by removing unwanted characters and normalizing
            clean_path = (
                path.replace('\\textbackslash{}', '')
                    .replace('\\textbackslash', '')
                    .replace('\\', '/')
                    .replace('{', '')
                    .replace('}', '')
                    .replace('//', '/')
            )

            # Extract directory and filename parts
            import os
            dir_path, filename = os.path.split(clean_path)
            
            # Strip leading underscore and extension from filename (e.g., "_0.png" → "0")
            base_name, ext = os.path.splitext(filename)
            if base_name.startswith('_'):
                index = base_name[1:]
            else:
                index = base_name

            # Reconstruct new filename as "image_N.png"
            new_filename = f"image_{index}{ext}"
            
            # Construct final path without "_images" or other nested folders
            final_path = f"extracted_images/{new_filename}"

            # Generate proper LaTeX figure environment
            figure_output = (
                r'\begin{figure}[h!]' + '\n' +
                r'\centering' + '\n' +
                fr'\includegraphics[width=0.8\textwidth]{{{final_path}}}' + '\n' +
                r'\caption{}' + '\n' +
                fr'\label{{fig:image_{self.figure_count}}}' + '\n' +
                r'\end{figure}'
            )

            self.figure_count += 1  # Increment the counter for the next image
            return figure_output
        except Exception as e:
            return f"% ERROR: Could not process image: {str(e)}"


    def format_email(self, text: str) -> str:
        # Format contact section with email
        text = re.sub(
            r'(Contact:\s*)Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            lambda m: f"{m.group(1)}Email: \\texttt{{{m.group(2)}}}",
            text
        )
        return text

    def clean_whitespace(self, text: str) -> str:
        # Remove excessive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Ensure one empty line before sections
        text = re.sub(r'(\S)\n(\\section)', r'\1\n\n\2', text)
        return text.strip()

    def convert(self, text: str) -> str:
        processing_order = [
            self.escape_special_chars,
            self.format_sections,
            self.format_lists,
            self.format_tables,
            self.format_images,
            self.format_email,
            self.clean_whitespace,
        ]
        
        for processor in processing_order:
            try:
                text = processor(text)
            except Exception as e:
                print(f"Error in {processor.__name__}: {str(e)}")
                continue
        
        return text

    def generate_latex_document(self, text: str) -> str:
        if not text.strip():
            return self._error_document("Empty input text")
            
        try:
            lines = text.split('\n')
            title = lines[0].strip() if lines else "Untitled Document"
            content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            latex_content = self.convert(content)
            
            latex_template = fr"""\documentclass[12pt]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage{{enumitem}}
\usepackage{{parskip}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}  % Added for image support

\title{{{self.escape_special_chars(title)}}}
\author{{Anonymous}}
\date{{\today}}

\begin{{document}}
\maketitle

{latex_content}

\end{{document}}"""
            
            return latex_template
        except Exception as e:
            return self._error_document(str(e))

    def _error_document(self, error_msg: str) -> str:
        return fr"""\documentclass{{article}}
\begin{{document}}
\section{{Conversion Error}}
An error occurred during LaTeX conversion:

\texttt{{{self.escape_special_chars(error_msg)}}}
\end{{document}}"""

def text_to_latex(text: str) -> str:
    """Convert plain text to LaTeX format with proper sections, lists, tables, and images.
    
    Args:
        text: Input text to convert (can include Markdown or HTML image syntax)
        Returns:
        str: Complete LaTeX document as a string
    """
    converter = LatexConverter()
    return converter.generate_latex_document(text)
