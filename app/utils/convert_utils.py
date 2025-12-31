
def structured_to_plaintext(data):
    """Convert structured resume data to plain text."""
    return structured_to_text(data)

def structured_to_text(data):
    lines = []

    full_name = data.get("full_name","").strip()
    title = data.get("title","").strip()
    if full_name:
        lines.append(f"Full name: {full_name}")
    if title:
        lines.append(f"Title: {title}")
    lines.append("")

    #Contact
    lines.append("Contact:")
    if data.get("email"):
        lines.append(data.get("email").strip())
    if data.get("phone"):
        lines.append(data.get("phone").strip())
    if data.get("website"):
        lines.append(f"Website: {data['website'].strip()}")
    if data.get("linkedin"):
        lines.append(f"Linkedin: {data['linkedin'].strip()}")
    lines.append("")

    # Summary
    summary = (data.get("summary") or "").strip()
    if summary:
        lines.append("summary:")
        lines.append(data.get("summary","").strip())
        lines.append("")

    # Skills
    skills = data.get("skills", [])
    if skills:
        lines.append("Skills:")
        if isinstance(skills, list):
            lines.append(",".join(skills))
        else:
            lines.append(str(skills))
        lines.append("")

    # Experience
    experience = data.get("experience",[])
    if experience:
        lines.append("Experience:")
        for e in experience:
            role = e.get("role","")
            company = e.get("company","")
            dates = e.get("dates","")
            desc = e.get("desc","")
            line = f"{role} at {company}".strip()
            if dates:
                line += f" ({dates})"
            if line:
                lines.append(line)
            if desc:
                lines.append(desc)
            lines.append("")

    # Education
    education = data.get("education",[])
    if education:
        lines.append("Education:")
        for ed in education:
            degree = ed.get("degree","")
            school = ed.get("school","")
            years = ed.get("years","")
            line = f"{degree} - {school}".strip(" -")
            if years:
                line += f" ({years})"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)

def form_to_structured(d):
    structured = {}

    structured["full_name"] = d.get("full_name","").strip()
    structured["title"] = d.get("title","").strip()
    structured["email"] = d.get("email","").strip()
    structured["phone"] = d.get("phone","").strip()
    structured["summary"] = d.get("summary","").strip()

    skills = d.get("skills","").strip()
    # Normalize skills: allow list or comma-separated string
    if isinstance(skills, list):
        # if coming from JS as list
        structured["skills"] = [s.strip() for s in skills if s.strip()]
    else:
        #comma separated string
        structured["skills"] = [s.strip() for s in skills.split(",") if s.strip()]

    # Experience
    structured["experience"] = []
    for i in range(1,6):
        company = d.get(f"exp_company_{i}","").strip()
        role = d.get(f"exp_role_{i}","").strip()
        dates = d.get(f"exp_dates_{i}","").strip()
        desc = d.get(f"exp_desc_{i}","").strip()

        if company or role or desc:
            structured["experience"].append({"company":company, "role":role, "dates":dates, "desc":desc})

    # Education
    structured["education"] = []
    for i in range(1,4):
        school = d.get(f"edu_school_{i}","").strip()
        degree = d.get(f"edu_degree_{i}","").strip()
        years = d.get(f"edu_years_{i}","").strip()

        if school or degree:
            structured["education"].append({"school":school, "degree":degree, "years":years})

    # Single fields (linkedin, website)
    structured["linkedin"] = d.get(f"linkedin","").strip()
    structured["website"] = d.get(f"website","").strip()

    return structured
