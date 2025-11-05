
def generate_docx(data):
    doc = Document()

    doc.add_heading(data.get("full_name", ""), 0)
    if data.get("title"):
        doc.add_paragraph(data.get("title"))

    # Contact Info
    doc.add_paragraph(f"Email: {data.get('email','')}".strip())
    doc.add_paragraph(f"Phone: {data.get('phone','')}".strip())
    if data.get("website"):
        doc.add_paragraph(f"Website: {data.get('website')}")
    if data.get("linkedin"):
        doc.add_paragraph(f"Linkedin: {data.get('linkedin')}")

    # Profile
    doc.add_paragraph()
    doc.add_heading("Profile", level=1)
    doc.add_paragraph(data.get("summary", ""))

    # Skills
    doc.add_paragraph()
    doc.add_heading("Skills", level=1)
    doc.add_paragraph(", ".join(data.get("skills",[])))

    # Experience
    doc.add_paragraph()
    doc.add_heading("Experience", level=1)
    for e in data.get("experience", []):
        doc.add_paragraph(f"{e.get('role','')} - {e.get('company','')} | {e.get('dates','')}")
        doc.add_paragraph(e.get("desc",""))

    # Education
    doc.add_paragraph()
    doc.add_heading("Education", level=1)
    for ed in data.get("education",[]):
        doc.add_paragraph(f"{ed.get('degree','')} - {ed.get('school','')} ({ed.get('years','')})")

    # QR
    qr_data = data.get("linkedin") or data.get("website")
    if qr_data:
        qr_img = qrcode.make(qr_data)
        bio = io.BytesIO()
        qr_img.save(bio, "PNG")
        bio.seek(0)
        # Insert QR image (docx wants a file-like or path)
        doc.add_page_break()
        doc.add_heading("Scan this QR to view online:", level=1)
        doc.add_picture(bio, width = Inches(2))

    out = io.BytesIO()
    doc.save(out)
    out.seek(0)
    return out