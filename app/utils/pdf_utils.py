
def generate_pdf_weasyprint(data):
    """
    Generate a PDF resume using WeasyPrint from rendered HTML.
    """
    # Render the resume template (you can change to any template you use)
    html_content = render_template("templates_variants/template_modern.html", data=data, preview=False)

    # Create an in-memory file
    pdf_io = io.BytesIO()

    # Optional: add a CSS file for consistent PDF styling
    css_path = os.path.join(BASE_DIR, 'static', 'css', 'pdf.css')
    css = CSS(filename=css_path) if os.path.exists(css_path) else None

    # Generate the PDF
    if css:
        HTML(string=html_content).write_pdf(pdf_io, stylesheets=[css])
    else:
        HTML(string=html_content).write_pdf(pdf_io)

    pdf_io.seek(0)
    return pdf_io