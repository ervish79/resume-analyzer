![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)


#  AI Resume Analyzer

An AI-powered Resume Screening System that analyzes resumes, matches skills with job roles, and provides improvement suggestions.

---

##  Features

- User Authentication (Login / Signup)
- Resume Skill Analysis
- Score Calculation
- PDF Report Generation
- Resume Ranking System
- User History & Score Graph
- Admin Dashboard
- OCR Support (for scanned resumes)

---

##  Tech Stack

- Python
- Streamlit
- SQLite
- PyPDF2
- Tesseract OCR
- Matplotlib

---

##  Live Demo

👉 https://resume-analyzer-eybdb9x2u5u9ztgpaisqyt.streamlit.app

---

## How It Works

1. User uploads resume (PDF)
2. Text is extracted using PyPDF2 + OCR
3. Skills are matched using keyword + synonym logic
4. Score is calculated based on matched skills
5. Results stored in SQLite database
6. Dashboard shows analytics and history

---

## Future Improvements

- AI-based semantic skill matching (NLP)
- Resume parsing using spaCy
- Job API integration (LinkedIn, Indeed)
- Cloud database (PostgreSQL)
- Role-based authentication (JWT)


---

## Architecture

User → Streamlit UI → Backend Logic → SQLite DB
                    ↓
               OCR + NLP Processing

---


## Why This Project?

Manual resume screening is time-consuming and inconsistent.
This project automates resume evaluation using AI techniques,
helping recruiters quickly identify the best candidates.

---

## Author

Hemant Kumar 
Computer Science Student  
GitHub: https://github.com/ervish79

## Installation

```bash
git clone https://github.com/ervish79/resume-analyzer.git
cd resume-analyzer
pip install -r requirements.txt
streamlit run app.py





