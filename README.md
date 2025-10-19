# my-first-project

This is also my firstt real web app from my one month class

# Resume Builder (Flask) — Full Project

Features:
- User registration/login (Flask-Login + SQLite)
- Live preview of resume using AJAX and iframe
- Multiple templates (two templates included)
- Save resumes to user accounts (stored in DB)
- Export options:
  - PDF (ReportLab)
  - DOCX (python-docx)
  - Plain-text (.txt)
  - JSON (.json) for ATS
- QR code linking to LinkedIn / portfolio included in PDF and DOCX
- Simple, ready-to-run project packaged into this ZIP

## How to run

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt