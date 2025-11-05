from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Resume, UploadedFile

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

@resume_bp.route("/compose", methods=['GET', 'POST'])
@login_required
def compose():
    """Compose a new resume."""
    db = SessionLocal()
    try:
        if request.method == "POST":
            form = request.form.to_dict(flat=False)
            simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}
            structured = form_to_structured(simple)

            if not structured.get("full_name"):
                flash("Please enter your name", "compose info")
                return redirect(url_for('compose'))

            html_preview = render_template("templates_variants/template_modern.html", data=structured, preview=True)

            resume = Resume(
                user_id=current_user.id,
                title=structured.get("full_name", "Untitled"),
                template=simple.get("template", "template_modern.html"),
                data_json=json.dumps(structured),
                html_preview=html_preview,
            )

            db.add(resume)
            db.commit()

            flash("Resume saved successfully!", "dashboard success")
            return redirect(url_for("dashboard"))

        templates_dir = os.path.join(BASE_DIR, 'templates', 'templates_variants')
        templates = os.listdir(templates_dir) if os.path.exists(templates_dir) else []
        return render_template('compose.html', templates=templates)

    finally:
        db.close()

@resume_bp.route("/preview", methods=['POST'])
@login_required
def preview():

    form_data = request.form.to_dict(flat=False)
    simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form_data.items()}

    template =simple.get("template", 'template_modern.html')
    allowed_templates_dir = os.path.join(BASE_DIR, 'templates', 'templates_variants')
    allowed_templates = set(os.listdir(allowed_templates_dir)) if os.path.exists(allowed_templates_dir) else set()

    if template not in allowed_templates:
        flash("Invalid template selected.", " compose danger")
        return jsonify({"error": "Invalid template selected."}), 400

    structured = form_to_structured(simple)
    html = render_template(f"templates_variants/{template}", data = structured, preview=True)

    return jsonify({"html": html})

@resume_bp.route("/save", methods=['POST'])
@login_required
def save():
    """Save a completed resume to the database."""
    db = SessionLocal()
    try:
        form = request.form.to_dict(flat=False)
        simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}

        template = simple.get("template", "template_modern.html")
        templates_dir = os.path.join(BASE_DIR, 'templates', 'templates_variants')
        allowed_templates = set(os.listdir(templates_dir)) if os.path.exists(templates_dir) else set()

        if template not in allowed_templates:
            flash("Invalid template selected.", "compose danger")
            return redirect(url_for("compose"))

        structured = form_to_structured(simple)
        html = render_template(f"templates_variants/{template}", data=structured, preview=True)

        resume = Resume(
            user_id=current_user.id,
            title=structured.get('full_name','Untitled'),
            template=template,
            data_json=json.dumps(structured),
            html_preview=html,
        )
        db.add(resume)
        db.commit()
        flash("Resume saved successfully!", "dashboard success")

        # Generate and save the PDF to disk
        pdf_io = generate_pdf_weasyprint(structured)
        pdf_filename = f"resume_{resume.id}.pdf"
        pdf_path = os.path.join(BASE_DIR, "static", "resumes", pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(pdf_io.read())

        # Optionally store path in database
        resume.pdf_path = pdf_path
        db.commit()

    except Exception as e:
        db.rollback()
        flash(f"Error saving resume: {e}", "danger")

    finally:
        db.close()

    return redirect(url_for('dashboard'))

@resume_bp.route("/resume/edit/<int:resume_id>", methods=["GET", "POST"])
@login_required
def edit_resume(resume_id):
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter_by(id=resume_id, user_id=current_user.id).first()
        if not resume:
            flash("Resume not found or access denied.", " danger")
            return redirect(url_for("dashboard"))

        data = json.loads(resume.data_json)

        if request.method == "POST":
            form = request.form.to_dict(flat=False)
            simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}
            structured = form_to_structured(simple)
            resume.data_json = json.dumps(structured)
            resume.html_preview = render_template(f"templates_variants/{resume.template}", data=structured, preview=True)

            # regenerate PDF
            pdf_io = generate_pdf_weasyprint(structured)
            with open(resume.pdf_path, "wb") as f:
                f.write(pdf_io.read())

            db.commit()
            flash("Resume updated successfully!", "success")
            return redirect(url_for("dashboard"))

        # Preload form with existing data
        return render_template("edit_resume.html", data=data, resume=resume)

    finally:
        db.close()

@resume_bp.route("/resume/delete/<int:resume_id>")
@login_required
def delete_resume(resume_id):
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter_by(id=resume_id, user_id=current_user.id).first()
        if not resume:
            flash("Resume not found or access denied.", "danger")
            return redirect(url_for("dashboard"))

        # Delete PDF file if exists
        if resume.pdf_path and os.path.exists(resume.pdf_path):
            os.remove(resume.pdf_path)

        db.delete(resume)
        db.commit()
        flash("Resume deleted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting resume: {e}", "danger")
    finally:
        db.close()

    return redirect(url_for("dashboard"))

@resume_bp.route("/resume/<int:resume_id>")
@login_required
def view_resume(resume_id):
    """Preview a specific resume."""
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter_by(id=resume_id, user_id=current_user.id).first()
        if not resume:
            flash("Resume not found or you don't have access.", "warning")
            return redirect(url_for("dashboard"))

        templates_dir = os.path.join(BASE_DIR, 'templates', 'templates_variants')
        allowed_templates = set(os.listdir(templates_dir)) if os.path.exists(templates_dir) else set()
        if resume.template not in allowed_templates:
            flash("Template file missing or invalid.", "danger")
            return redirect(url_for("dashboard"))

        try:
            data = json.loads(resume.data_json)
        except json.JSONDecodeError:
            flash("Could not read resume.", "danger")
            return redirect(url_for("dashboard"))

        return render_template(f"templates_variants/{resume.template}", data=data, preview=False)

    except Exception as e:
        flash(f"Error loading resume: {e}", "danger")
        return redirect(url_for("dashboard"))

    finally:
        db.close()

@resume_bp.route("/download/<int:resume_id>/<fmt>")
@login_required
def download_resume(resume_id, fmt):
    """Download a resume."""
    db = SessionLocal()
    print("Trying to download resume:", resume_id, fmt)
    try:
        r = db.query(Resume).filter_by(id=resume_id, user_id=current_user.id).first()
        if not r:
            flash("Resume not found or you don't have permission.", "danger")
            return redirect(url_for("dashboard"))

        data = json.loads(r.data_json)
        title = (data.get("full_name") or "resume").replace("_", " ")

        if fmt == "json":
            bio = io.BytesIO(json.dumps(data, indent=2).encode("utf-8"))
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name=f"{title}.json", mimetype="application/json")

        elif fmt == "txt":
            txt = structured_to_plaintext(data)
            bio = io.BytesIO(txt.encode("utf-8"))
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name=f"{title}.txt", mimetype="text/plain")

        elif fmt == "docx":
            docx_io = generate_docx(data)
            docx_io.seek(0)
            return send_file(docx_io, as_attachment=True, download_name=f"{title}.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        elif fmt == "pdf":
            pdf_io = generate_pdf_weasyprint(data)
            pdf_io.seek(0)
            return send_file(pdf_io, as_attachment=True, download_name=f"{title}.pdf", mimetype="application/pdf")

        else:
            flash(f"Unsupported download format.", "danger")
            return redirect(url_for("dashboard"))

    except Exception as e:
        print("Download error:", e)
        flash(f"Error generating resume: {e}", "danger")
        return redirect(url_for("dashboard"))
    finally:
        db.close()
