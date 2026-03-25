from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
import pytesseract
from pdf2image import convert_from_bytes
import io
import os
import re

# =========================
# CONFIGURATION (CROSS PLATFORM)
# =========================

# Set paths only for Windows (local system)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\Release-25.12.0-0\poppler-25.12.0\Library\bin"
else:
    # For deployment (Linux / Streamlit Cloud)
    POPPLER_PATH = None


# =========================
# TEXT CLEANING FUNCTION
# =========================
def clean_text(text):
    """
    Clean extracted text by removing special characters
    and extra spaces for better matching.
    """
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower()


# =========================
# TEXT EXTRACTION FUNCTION
# =========================
def extract_text(file):
    """
    Extract text from PDF.
    Step 1: Try direct PDF extraction
    Step 2: If no text found, use OCR
    """

    text = ""
    file_bytes = file.read()

    # Step 1: Direct PDF extraction
    try:
        pdf = PdfReader(io.BytesIO(file_bytes))
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content
    except Exception:
        pass

    # Step 2: OCR if no text found
    if not text.strip():
        try:
            if POPPLER_PATH:
                images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
            else:
                images = convert_from_bytes(file_bytes)

            for img in images:
                img = img.convert("L")  # Convert to grayscale
                text += pytesseract.image_to_string(img)

        except Exception as e:
            print("OCR ERROR:", e)

    return clean_text(text)


# =========================
# SKILL EXPANSION FUNCTION
# =========================
def expand_skills(skills):
    """
    Expand skills using synonyms.
    Example: "machine learning" -> ["machine learning", "ml"]
    """

    synonyms = {
        "machine learning": ["ml"],
        "data analysis": ["data analytics"],
        "python": ["py"],
        "numpy": ["np"],
        "pandas": [],
        "statistics": ["stats"]
    }

    expanded = {}

    for skill in skills:
        expanded[skill] = [skill] + synonyms.get(skill, [])

    return expanded


# =========================
# SCORE CALCULATION
# =========================
def calculate_score(resume_text, skills):
    """
    Calculate score based on matched skills.
    """

    resume_text = clean_text(resume_text)
    expanded_skills = expand_skills(skills)

    matched = 0

    for skill, variations in expanded_skills.items():
        for variant in variations:
            words = variant.split()

            if all(word in resume_text for word in words):
                matched += 1
                break

    score = (matched / len(skills)) * 100
    return round(score, 2)


# =========================
# SKILL ANALYSIS
# =========================
def skill_analysis(resume_text, skills):
    """
    Return list of found and missing skills.
    """

    resume_text = clean_text(resume_text)
    expanded_skills = expand_skills(skills)

    found = []
    missing = []

    for skill, variations in expanded_skills.items():
        matched = False

        for variant in variations:
            words = variant.split()

            if all(word in resume_text for word in words):
                found.append(skill)
                matched = True
                break

        if not matched:
            missing.append(skill)

    return found, missing


# =========================
# PDF REPORT GENERATION
# =========================
def generate_pdf_report(file_buffer, score, found, missing):
    """
    Generate PDF report in memory.
    """

    doc = SimpleDocTemplate(file_buffer, pagesize=letter)

    content = []

    content.append(Paragraph(f"<b>Resume Score:</b> {score}/100", None))
    content.append(Paragraph(f"<b>Skills Found:</b> {', '.join(found)}", None))
    content.append(Paragraph(f"<b>Skills Missing:</b> {', '.join(missing)}", None))

    doc.build(content)