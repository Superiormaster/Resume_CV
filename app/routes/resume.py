from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from app.extensions import db
from app.models import Resume, UploadedFile
from app.utils.pdf_utils import generate_pdf_weasyprint
from app.utils.data_utils import generate_docx
from app.utils.convert_utils import form_to_structured, structured_to_plaintext
import os, io, json, base64
from config import BASE_DIR
from werkzeug.utils import secure_filename

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_photo(file_storage, dest_dir, prefix="photo"):
    """Save uploaded photo and return web-accessible static path (relative to static/)"""
    if not file_storage or file_storage.filename == "":
      return None

    filename = secure_filename(file_storage.filename)

    # create unique-ish name
    name, ext = os.path.splitext(filename)
    new_name = f"{prefix}_{int.from_bytes(os.urandom(4), 'big')}{ext}"

    upload_dir = os.path.join(dest_dir)
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, new_name)
    file_storage.save(full_path)

    # return path relative to the static folder so templates can use url_for
    rel_path = os.path.relpath(full_path, os.path.join(BASE_DIR, 'static'))
    return rel_path.replace(os.path.sep, '/')

@resume_bp.route("/api/user_resumes")
def user_resumes():
    resumes = Resume.query.all()
    # Return only id and title (or name)
    data = [{"id": r.id, "title": r.title} for r in resumes]
    return jsonify(data)
    
@resume_bp.route('/templates')
def templates():
    templates_dir = os.path.join(
        current_app.root_path,
        'templates',
        'templates_variants'
    )

    templates = os.listdir(templates_dir)
    return render_template('resume/templates.html', templates=templates)
    
@resume_bp.route('/compose', methods=['GET', 'POST'])
@resume_bp.route('/compose/<template>', methods=['GET', 'POST'])
def compose(template=None):
  templates_dir = os.path.join(
    current_app.root_path,
    "templates",
    "templates_variants"
  )
  templates = os.listdir(templates_dir) if os.path.exists(templates_dir) else []

  # fallback template
  if template is None:
    template = templates[0] if templates else "template_modern.html"

  if template not in templates:
    abort(404)

  if request.method == "POST":
    form = request.form.to_dict(flat=False)
    simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}

    photo = request.files.get('photo')
    if photo and allowed_file(photo.filename):
        rel = save_uploaded_photo(photo, os.path.join(BASE_DIR, 'static', 'uploads'), prefix='resume')

        if rel:
            # store the static-relative URL in the structured data so render_template can use it
            simple['photo_url'] = url_for('static', filename=rel)

    structured = form_to_structured(simple)

    if not structured.get("full_name"):
        flash("Please enter your name", "compose info")
        return redirect(url_for('resume.compose'))

    # compare this two
    template_name = simple.get('template', 'template_modern.html')
    html_preview = render_template(f"templates_variants/{template_name}", data=structured, preview=True)

    resume = Resume(
        title=structured.get("full_name", "Untitled"),
        template=simple.get("template", "template_modern.html"),
        data_json=json.dumps(structured),
        html_preview=html_preview,
        pdf_path=None
    )

    db.session.add(resume)
    db.session.commit()

    # Generate and save the PDF to disk
    pdf_io = generate_pdf_weasyprint(structured)
    pdf_filename = f"resume_{resume.id}.pdf"
    pdf_path = os.path.join(BASE_DIR, "static", "resumes", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(pdf_path, "wb") as f:
        f.write(pdf_io.read())

    # Optionally store path in database
    resume.pdf_path = pdf_path
    db.session.commit()

    flash("Resume saved successfully!", "dashboard success")
    return redirect(url_for("dashboard_bp.dashboard"))

  return render_template(
    'resume/compose.html',
    templates=templates,
    selected_template=template
  )

@resume_bp.route("/preview", methods=['POST'])
def preview():
  form_data = request.form.to_dict(flat=False)
  simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form_data.items()}

  structured = form_to_structured(simple)
  
  structured["experience"] = []
  for i in range(5):
      role = simple.get(f"exp_role_{i}")
      if role:
          structured["experience"].append({
              "role": role,
              "company": simple.get(f"exp_company_{i}"),
              "dates": simple.get(f"exp_dates_{i}"),
              "desc": simple.get(f"exp_desc_{i}")
          })
  
  structured["education"] = []
  for i in range(3):
      degree = simple.get(f"edu_degree_{i}")
      if degree:
          structured["education"].append({
              "degree": degree,
              "school": simple.get(f"edu_school_{i}"),
              "years": simple.get(f"edu_years_{i}")
          })
          
  photo = request.files.get('photo')
  if photo and allowed_file(photo.filename):

    # read bytes and base64 encode - safe for inline preview
    photo_rel = save_uploaded_photo(
        file_storage=photo,
        dest_dir=os.path.join(BASE_DIR, 'static', 'uploads'),
        prefix='resume_preview'

    )

    if photo_rel:
        structured['photo_url'] = url_for('static', filename=photo_rel)

        # Absolute path for PDF generator if needed
        structured['_photo_file'] = os.path.join(BASE_DIR, 'static', photo_rel)

        # Base64 for inline preview
        photo.seek(0)  # rewind file pointer
        photo_bytes = photo.read()
        b64 = base64.b64encode(photo_bytes).decode('ascii')
        structured['photo_dataurl'] = f"data:{photo.mimetype};base64,{b64}"

    else:
        # Keep existing photo_url if present
        structured['photo_url'] = structured.get('photo_url')
  template = simple.get("template", 'template_modern.html').strip()
  templates_dir = os.path.join(current_app.root_path, "templates", "templates_variants")
  allowed_templates = set(os.listdir(templates_dir)) if os.path.exists(templates_dir) else set()
  if template not in allowed_templates:
    template = 'template_modern.html'

  html = render_template(f"templates_variants/{template}", data = structured, preview=True)

  return jsonify({"html": html})
  
@resume_bp.route("/save", methods=['POST'])
def save():
    """Save a completed resume to the database."""
    form = request.form.to_dict(flat=False)
    simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}

    templates_dir = os.path.join(current_app.root_path, 'templates', 'templates_variants')
    allowed_templates = set(os.listdir(templates_dir)) if os.path.exists(templates_dir) else set()
    allowed_templates = {t.strip() for t in allowed_templates}

    template = simple.get("template", "").strip()

    if template not in allowed_templates:
        flash("Invalid template selected.", "compose danger")
        return redirect(url_for("resume.compose"))

    # --- HANDLE PHOTO ---
    photo = request.files.get("photo")
    if photo and allowed_file(photo.filename):
        rel = save_uploaded_photo(photo, os.path.join(BASE_DIR, 'static', 'uploads'), prefix='resume')
        if rel:
            simple['photo_url'] = url_for('static', filename=rel)
    else:
        # Continue without photo
        simple['photo_url'] = None

    # --- CONVERT FORM ---
    structured = form_to_structured(simple)

    # --- GENERATE HTML ---
    html = render_template(f"templates_variants/{template}", data=structured, preview=True)

    # --- SAVE RESUME IN DB ---
    resume = Resume(
        title=structured.get('full_name', 'Untitled'),
        template=template,
        data_json=json.dumps(structured),
        html_preview=html,
        pdf_path=None
    )
    db.session.add(resume)
    db.session.commit()

    # --- GENERATE PDF ---
    pdf_io = generate_pdf_weasyprint(structured)
    pdf_filename = f"resume_{resume.id}.pdf"
    pdf_path = os.path.join(BASE_DIR, "static", "resumes", pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    with open(pdf_path, "wb") as f:
        f.write(pdf_io.read())

    resume.pdf_path = pdf_path
    db.session.commit()

    flash("Resume saved successfully!", "dashboard success")
    return redirect(url_for("dashboard_bp.dashboard"))

@resume_bp.route("/resume/edit/<int:resume_id>", methods=["GET", "POST"])
def edit_resume(resume_id):
  resume = db.session.query(Resume).filter_by(id=resume_id).first()

  if not resume:
    flash("Resume not found or access denied.", " danger")
    return redirect(url_for("dashboard_bp.dashboard"))
  try:
    data = json.loads(resume.data_json)

  except Exception:
        data = {}

  if request.method == "POST":
    form = request.form.to_dict(flat=False)
    simple = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in form.items()}

    # allow replacing photo when editing
    rel = None   # ADD THIS
    photo = request.files.get('photo')
    if photo and allowed_file(photo.filename):
      rel = save_uploaded_photo(photo, os.path.join(BASE_DIR, 'static', 'uploads'), prefix=f'resume_{resume.id}')
      if rel:
        simple['photo_url'] = url_for('static', filename=rel)
    else:
      simple["photo_url"] = data.get("photo_url")
      
      experience = []
      for i in range(5):
          role = request.form.get(f"exp_role_{i}")
          if role:
              experience.append({
                  "role": role,
                  "company": request.form.get(f"exp_company_{i}"),
                  "dates": request.form.get(f"exp_dates_{i}"),
                  "desc": request.form.get(f"exp_desc_{i}")
              })
      
      education = []
      for i in range(3):
          degree = request.form.get(f"edu_degree_{i}")
          if degree:
              education.append({
                  "degree": degree,
                  "school": request.form.get(f"edu_school_{i}"),
                  "years": request.form.get(f"edu_years_{i}")
              })
              
      structured = form_to_structured(simple)
      structured["experience"] = experience
      structured["education"] = education

      resume.data_json = json.dumps(structured)
      resume.html_preview = render_template(f"templates_variants/{resume.template}", data=structured, preview=True)
      
      # regenerate PDF
      pdf_io = generate_pdf_weasyprint(structured)
      pdf_io.seek(0)
      with open(resume.pdf_path, "wb") as f:
          f.write(pdf_io.read())

      db.session.commit()
      flash("Resume updated successfully!", "success")
      return redirect(url_for("dashboard_bp.dashboard"))

  # Preload form with existing data
  return render_template(
    "edit_resume.html",
    data=data,
    resume=resume,
    resume_id=resume.id,
    experiences=data.get("experience", []),
    educations=data.get("education", [])
  )

@resume_bp.route("/resume/delete/<int:resume_id>")
def delete_resume(resume_id):
  resume = db.session.query(Resume).filter_by(id=resume_id).first()
  if not resume:
    flash("Resume not found or access denied.", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))

# Delete PDF file if exists
  if resume.pdf_path and os.path.exists(resume.pdf_path):
    try:
        os.remove(resume.pdf_path)
    except Exception:
        pass

  db.session.delete(resume)
  db.session.commit()

  flash("Resume deleted successfully!", "success")
  return redirect(url_for("dashboard_bp.dashboard"))

@resume_bp.route("/resume/<int:resume_id>")
def view_resume(resume_id):
  """Preview a specific resume."""

  resume = Resume.query.filter_by(id=resume_id).first()
  if not resume:
    flash("Resume not found or you don't have access.", "warning")
    return redirect(url_for("dashboard_bp.dashboard"))

  templates_dir = os.path.join(current_app.root_path, 'templates', 'templates_variants')
  allowed_templates = set(os.listdir(templates_dir)) if os.path.exists(templates_dir) else set()

  if resume.template.strip() not in allowed_templates:
    flash("Template file missing or invalid.", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))
  try:
    data = json.loads(resume.data_json)
  except json.JSONDecodeError:
    flash("Could not read resume.", "danger")

    return redirect(url_for("dashboard_bp.dashboard"))
  return render_template(f"templates_variants/{resume.template.strip()}", data=data, preview=False)

@resume_bp.route("/download/<int:resume_id>/<fmt>")
def download_resume(resume_id, fmt):
  """Download a resume."""

  resume = Resume.query.filter_by(id=resume_id).first()
  if not resume:
    flash("Resume not found or you don't have permission.", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))
  data = json.loads(resume.data_json)
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
    flash(f"Unsupported Download Format.", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))