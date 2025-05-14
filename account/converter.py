def text_to_latex(text):
    # Basic conversions (customize as needed)
    latex = text.replace("\n\n", "\n\n\\par\n")  # Paragraphs
    latex = latex.replace("* ", "\\item ")       # Bullet points
    latex = latex.replace("**", "\\textbf{")     # Bold
    latex = latex.replace("__", "\\textit{")     # Italic
    return f"""
\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\begin{{document}}
{latex}
\\end{{document}}
"""