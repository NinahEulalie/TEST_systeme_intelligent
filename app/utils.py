import pdfplumber

def extract_text_from_pdf(pdf_file):
    """Prend un fichier PDF et retourne le texte brut"""
    full_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text.strip()
