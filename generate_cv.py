#!/usr/bin/env python3

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

BUILD_DIR = "build"

# ── Dataclasses ──────────────────────────────────────────────────────

@dataclass
class Dates:
    start: str
    end: Optional[str] = None


@dataclass
class Experience:
    role: str
    company: str
    dates: Dates
    summary: str
    highlights: list[str] = field(default_factory=list)
    stack: list[str] = field(default_factory=list)


@dataclass
class SkillCategory:
    name: str
    items: list[str] = field(default_factory=list)


@dataclass
class InitialEducation:
    degree: str
    school: str
    location: str = ""
    dates: Optional[Dates] = None
    details: str = ""


@dataclass
class ProfessionalEducation:
    course: str
    organization: str
    location: str = ""
    dates: Optional[Dates] = None


@dataclass
class FunctionalSkill:
    category: str
    caption: str
    details: list[str] = field(default_factory=list)


@dataclass
class TechnicalSkill:
    left_name: str
    right_name: str
    left_items: list[str] = field(default_factory=list)
    right_items: list[str] = field(default_factory=list)


@dataclass
class Language:
    language: str
    level: str = ""


@dataclass
class Hobby:
    activity: str
    details: str = ""


@dataclass
class PersonalInfo:
    name: dict
    title: str
    career_start: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    birth_date: str = ""
    nationality: str = ""
    driver_license: bool = False
    marital_status: str = ""
    github: str = ""
    linkedin: str = ""
    photo: str = ""


@dataclass
class CVData:
    meta: dict
    personal_info: PersonalInfo
    skills: list[SkillCategory]
    experience: list[Experience]
    initial_education: list[InitialEducation] = field(default_factory=list)
    professional_education: list[ProfessionalEducation] = field(default_factory=list)
    functional_skills: list[FunctionalSkill] = field(default_factory=list)
    technical_skills: list[TechnicalSkill] = field(default_factory=list)
    languages: list[Language] = field(default_factory=list)
    hobbies: list[Hobby] = field(default_factory=list)


# ── Helpers ──────────────────────────────────────────────────────────

MONTHS_FR = {
    "01": "janvier", "02": "février", "03": "mars", "04": "avril",
    "05": "mai", "06": "juin", "07": "juillet", "08": "août",
    "09": "septembre", "10": "octobre", "11": "novembre", "12": "décembre",
}


def escape_latex(text: str) -> str:
    mapping = [
        ("\\", "\\textbackslash{}"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("%", "\\%"),
        ("_", "\\_"),
        ("&", "\\&"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for old, new in mapping:
        text = text.replace(old, new)
    return text


def unescape_latex(text: str) -> str:
    mapping = [
        ("\\textbackslash{}", "\\"),
        ("\\textasciitilde{}", "~"),
        ("\\textasciicircum{}", "^"),
        ("\\{", "{"),
        ("\\}", "}"),
        ("\\%", "%"),
        ("\\_", "_"),
        ("\\&", "&"),
        ("\\$", "$"),
        ("\\#", "#"),
    ]
    for old, new in mapping:
        text = text.replace(old, new)
    return text


def format_date(date_str: str) -> str:
    if not date_str:
        return ""
    parts = date_str.split("-")
    if len(parts) == 2:
        year, month = parts
        month_name = MONTHS_FR.get(month, month)
        return f"{month_name} {year}"
    return date_str


def format_date_range(start: str, end: Optional[str]) -> str:
    s = format_date(start)
    if end is None:
        return s
    e = format_date(end)
    return f"{s} à {e}"


def compute_duration(start: str, end: Optional[str]) -> str:
    start_parts = start.split("-")
    start_year = int(start_parts[0])
    start_month = int(start_parts[1]) if len(start_parts) >= 2 else 1

    if end is None:
        from datetime import date
        today = date.today()
        end_year, end_month = today.year, today.month
    else:
        end_parts = end.split("-")
        end_year = int(end_parts[0])
        end_month = int(end_parts[1]) if len(end_parts) >= 2 else 1

    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    if start_month != end_month:
        total_months += 1
    years, months = total_months // 12, total_months % 12
    parts = []
    if years > 0:
        parts.append(f"{years} an{'s' if years > 1 else ''}")
    if months > 0:
        parts.append(f"{months} mois")
    return " ".join(parts) if parts else ""


def compute_experience_years(career_start: str) -> int:
    from datetime import date
    today = date.today()
    parts = career_start.split("-")
    start_year = int(parts[0])
    start_month = int(parts[1]) if len(parts) >= 2 else 1
    years = today.year - start_year
    if today.month < start_month:
        years -= 1
    return max(years, 0)


def obfuscate_phone(text: str) -> str:
    """Insert {} after each pair of digits to break text extraction.
    {} is a no-op empty group — no visual effect, zero-width,
    safe in any LaTeX context (text, PDF strings, hrefs, etc.)."""
    import re
    return re.sub(r"(\d{2})", r"\1{}", text)


def email_parts(email: str) -> tuple[str, str]:
    """Return (clean_email, display_latex) from stored format 'user (at) domain'."""
    parts = email.split(" (at) ")
    if len(parts) == 2:
        clean = parts[0] + "@" + parts[1]
        display = f"{parts[0]} \\includegraphics[height=0.8em]{{../at.pdf}} {parts[1]}"
    else:
        clean = email
        display = email
    return clean, display


def stack_to_latex(stack: list[str]) -> str:
    if not stack:
        return ""
    escaped = [escape_latex(s) for s in stack]
    return ", ".join(escaped)


# ── Validator ─────────────────────────────────────────────────────────

DATE_RE = r"^\d{4}(-\d{2})?$"


def validate_cv_data(data: CVData) -> list[str]:
    errors = []
    pi = data.personal_info

    if not pi.name.get("first"):
        errors.append("personal_info.name.first: required")
    if not pi.name.get("family"):
        errors.append("personal_info.name.family: required")
    if not pi.title:
        errors.append("personal_info.title: required")

    for i, exp in enumerate(data.experience):
        prefix = f"experience[{i}]"
        if not exp.role:
            errors.append(f"{prefix}.role: required")
        if not exp.company:
            errors.append(f"{prefix}.company: required")
        if not exp.dates.start:
            errors.append(f"{prefix}.dates.start: required")

    for i, edu in enumerate(data.initial_education):
        if not edu.degree:
            errors.append(f"initial_education[{i}].degree: required")
        if not edu.school:
            errors.append(f"initial_education[{i}].school: required")

    for i, pe in enumerate(data.professional_education):
        if not pe.course:
            errors.append(f"professional_education[{i}].course: required")
        if not pe.organization:
            errors.append(f"professional_education[{i}].organization: required")

    for i, fs in enumerate(data.functional_skills):
        if not fs.category:
            errors.append(f"functional_skills[{i}].category: required")
        if not fs.caption:
            errors.append(f"functional_skills[{i}].caption: required")

    for i, ts in enumerate(data.technical_skills):
        if not ts.left_name:
            errors.append(f"technical_skills[{i}].left_name: required")
        if not ts.right_name:
            errors.append(f"technical_skills[{i}].right_name: required")

    for i, lg in enumerate(data.languages):
        if not lg.language:
            errors.append(f"languages[{i}].language: required")

    for i, hb in enumerate(data.hobbies):
        if not hb.activity:
            errors.append(f"hobbies[{i}].activity: required")

    return errors


# ── Load & Validate ──────────────────────────────────────────────────

def load_cv(path: str) -> CVData:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    pi = raw["personal_info"]
    title = pi.get("title", "")
    career_start = pi.get("career_start", "")
    if career_start and "{exp_years}" in title:
        years = compute_experience_years(career_start)
        title = title.replace("{exp_years}", str(years))
    personal_info = PersonalInfo(
        name=pi["name"],
        title=escape_latex(title),
        career_start=career_start,
        phone=escape_latex(pi.get("phone", "")),
        email=escape_latex(pi.get("email", "")),
        address=escape_latex(pi.get("address", "")),
        birth_date=pi.get("birth_date", ""),
        nationality=pi.get("nationality", ""),
        driver_license=pi.get("driver_license", False),
        marital_status=escape_latex(pi.get("marital_status", "")),
        github=pi.get("github", ""),
        linkedin=pi.get("linkedin", ""),
        photo=escape_latex(pi.get("photo", "")),
    )

    skills = [
        SkillCategory(
            name=escape_latex(cat["name"]),
            items=[escape_latex(item) for item in cat.get("items", [])],
        )
        for cat in raw.get("skills", {}).get("categories", [])
    ]

    experience = []
    for exp in raw.get("experience", []):
        d = exp["dates"]
        highlights = [escape_latex(h) for h in exp.get("highlights", [])]
        stack = [escape_latex(s) for s in exp.get("stack", [])]
        experience.append(Experience(
            role=escape_latex(exp["role"]),
            company=escape_latex(exp["company"]),
            dates=Dates(start=d["start"], end=d.get("end")),
            summary=escape_latex(exp.get("summary", "")),
            highlights=highlights,
            stack=stack,
        ))

    initial_education = []
    for edu in raw.get("initial_education", []):
        d = edu.get("dates")
        initial_education.append(InitialEducation(
            degree=escape_latex(edu["degree"]),
            school=escape_latex(edu["school"]),
            location=escape_latex(edu.get("location", "")),
            dates=Dates(start=d["start"], end=d.get("end")) if d else None,
            details=escape_latex(edu.get("details", "")),
        ))

    professional_education = []
    for pe in raw.get("professional_education", []):
        d = pe.get("dates")
        professional_education.append(ProfessionalEducation(
            course=escape_latex(pe["course"]),
            organization=escape_latex(pe["organization"]),
            location=escape_latex(pe.get("location", "")),
            dates=Dates(start=d["start"], end=d.get("end")) if d else None,
        ))

    functional_skills = [
        FunctionalSkill(
            category=escape_latex(fs["category"]),
            caption=escape_latex(fs["caption"]),
            details=[escape_latex(d) for d in fs.get("details", [])],
        )
        for fs in raw.get("functional_skills", [])
    ]

    technical_skills = [
        TechnicalSkill(
            left_name=escape_latex(ts["left_name"]),
            left_items=[escape_latex(i) for i in ts.get("left_items", [])],
            right_name=escape_latex(ts["right_name"]),
            right_items=[escape_latex(i) for i in ts.get("right_items", [])],
        )
        for ts in raw.get("technical_skills", [])
    ]

    languages = [
        Language(
            language=escape_latex(lg["language"]),
            level=escape_latex(lg.get("level", "")),
        )
        for lg in raw.get("languages", [])
    ]

    hobbies = [
        Hobby(
            activity=escape_latex(hb["activity"]),
            details=escape_latex(hb.get("details", "")),
        )
        for hb in raw.get("hobbies", [])
    ]

    return CVData(
        meta=raw.get("meta", {}),
        personal_info=personal_info,
        skills=skills,
        experience=experience,
        initial_education=initial_education,
        professional_education=professional_education,
        functional_skills=functional_skills,
        technical_skills=technical_skills,
        languages=languages,
        hobbies=hobbies,
    )


# ── ModernCV Generator ───────────────────────────────────────────────

def render_moderncv(data: CVData) -> str:
    pi = data.personal_info
    license = "\\\\ permis B" if pi.driver_license else ""
    extra = "\\\\ né en {} {} \\\\ {} \\\\ nationalité {}".format(
        escape_latex(pi.birth_date),
        license,
        escape_latex(pi.marital_status),
        escape_latex(pi.nationality),
    )

    lines = []
    a = lines.append

    a(r"\documentclass[11pt,a4paper,sans]{moderncv}")
    a(r"\moderncvstyle{classic}")
    a(r"\moderncvcolor{blue}")
    a(r"\usepackage[utf8]{inputenc}")
    a(r"\usepackage[scale=0.8]{geometry}")
    a(r"\setlength{\hintscolumnwidth}{2.5cm}")
    a(r"\newcommand{\company}[1]{\textbf{\textcolor{color1}{#1}}}")
    a(r"\usepackage{fontawesome5}")
    a(r"\newcommand{\cvDateMarker}{\faCalendar[regular]}")
    a(r"\usepackage{qrcode}")
    a("")
    full_name = unescape_latex(pi.name["first"] + " " + pi.name["family"])
    raw_title = unescape_latex(pi.title)
    repo_url = pi.github.rstrip("/") + "/cvpoly"
    a(r"\AtBeginDocument{\hypersetup{")
    a(r"  pdfauthor={{{}}},".format(full_name))
    a(r"  pdftitle={{CV - {}}},".format(raw_title))
    a(r"  pdfsubject={{CV - {}}},".format(full_name))
    a(r"  pdfkeywords={{CV, {}}}".format(repo_url))
    a(r"}}")
    a("")
    a(r"\firstname{{{}}}".format(escape_latex(pi.name["first"])))
    a(r"\familyname{{{}}}".format(escape_latex(pi.name["family"])))
    a(r"\title{{{}}}".format(pi.title))
    a(r"\address{{}}{{}}{{{}}}".format(escape_latex(pi.address)))
    a(r"\mobile{{{}}}".format(obfuscate_phone(pi.phone)))
    clean_email, display_email = email_parts(pi.email)
    a(r"\renewcommand*{\emaillink}[1]{\href{mailto:%s}{\texttt{%s}}}" % (clean_email, display_email))
    a(r"\email{%s}" % clean_email)
    a(r"\extrainfo{{{}}}".format(extra))
    if pi.photo:
        a(r"\photo[90pt][0pt]{{../{}}}".format(pi.photo))
    a("")
    a(r"\begin{document}")
    a(r"\makecvtitle")
    a("")

    # ── Expériences ──
    a(r"\section{Expériences professionnelles}")
    for i, exp in enumerate(data.experience):
        if i > 0:
            a(r"\vspace{1.0ex}")
        dates = format_date_range(exp.dates.start, exp.dates.end)
        duration = compute_duration(exp.dates.start, exp.dates.end)
        dates_label = f"\\cvDateMarker~{dates}\\\\({duration})" if duration else f"\\cvDateMarker~{dates}"
        highlights_block = ""
        if exp.highlights:
            items = "%\n".join(r"\item {}%".format(h) for h in exp.highlights)
            highlights_block = "%\n{}".format(items) if items else ""
        stack_str = stack_to_latex(exp.stack) if exp.stack else ""
        body = f"\\color{{color2}}{exp.summary}"
        if highlights_block:
            body += "%\n\\begin{{itemize}}%\n{}%\n\\end{{itemize}}".format(highlights_block)
        if stack_str:
            body += "%\n{{\\small\\textbf{{Stack~:}}}} {}".format(stack_str)
        a(r"\cventry{{{}}}{{{}}}{{\company{{{}}}}}{{}}{{}}{{{}}}".format(dates_label, exp.role, exp.company, body))
    a("")

    # ── Formations professionnelles ──
    if data.professional_education:
        a(r"\section{Formations professionnelles}")
        for pe in data.professional_education:
            dates = ""
            if pe.dates:
                dates = format_date_range(pe.dates.start, pe.dates.end)
            a(r"\cventry{{{}}}{{{}}}{{{}}}{{{}}}{{}}{{}}%".format(
                dates, pe.course, pe.organization,
                pe.location if pe.location else "",
            ))
        a("")

    # ── Savoirs-faire ──
    if data.functional_skills:
        a(r"\section{Savoirs-faire}")
        for fs in data.functional_skills:
            comment_parts = []
            for d in fs.details:
                comment_parts.append("{}".format(d))
            comment = "\\\\\n".join(comment_parts) if comment_parts else ""
            a(r"\cvitemwithcomment{{{}}}{{{}}}{{{}}}%".format(fs.category, fs.caption, comment))
        a("")

    # ── Compétences techniques ──
    if data.technical_skills:
        a(r"\section{Compétences techniques}")
        for ts in data.technical_skills:
            left_items_str = ", ".join(ts.left_items)
            right_items_str = ", ".join(ts.right_items)
            a(r"\cvdoubleitem{{{}}}{{{}}}{{{}}}{{{}}}".format(
                ts.left_name, left_items_str, ts.right_name, right_items_str
            ))
        a("")


    # ── Formation initiale ──
    a(r"\section{Formation initiale}")
    for edu in data.initial_education:
        dates = ""
        if edu.dates:
            dates = format_date_range(edu.dates.start, edu.dates.end)
        a(r"\cventry{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{}}%".format(
            dates, edu.degree, edu.school,
            edu.location if edu.location else "",
            edu.details if edu.details else "",
        ))
    a("")

    # ── Langues ──
    if data.languages:
        a(r"\section{Langues}")
        for lg in data.languages:
            a(r"\cvitem{{{}}}{{{}}}".format(lg.language, lg.level))
        a("")

    # ── Loisirs ──
    if data.hobbies:
        a(r"\section{Loisirs}")
        for hb in data.hobbies:
            a(r"\cvitem{{{}}}{{{}}}".format(hb.activity, hb.details))
        a("")


    # ── QR Code ──
    a(r"\section{Références}")
    a(r"\cvitem{Code source}{\qrcode[height=2cm]{%s}\newline\url{%s}}" % (repo_url, repo_url))
    a("")

    a(r"\end{document}")
    return "\n".join(lines)


# ── AltaCV Generator ─────────────────────────────────────────────────

def render_altacv(data: CVData) -> str:
    pi = data.personal_info
    lines = []
    a = lines.append

    a(r"\documentclass[10pt,a4paper,ragged2e,withhyper]{altacv}")
    a(r"\geometry{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}")
    a(r"\usepackage{paracol}")
    a("")
    a(r"\iftutex")
    a(r"  \setmainfont{Roboto Slab}")
    a(r"  \setsansfont{Lato}")
    a(r"  \renewcommand{\familydefault}{\sfdefault}")
    a(r"\fi")
    a("")
    a(r"\definecolor{SlateGrey}{HTML}{2E2E2E}")
    a(r"\definecolor{LightGrey}{HTML}{666666}")
    a(r"\definecolor{DarkPastelRed}{HTML}{450808}")
    a(r"\definecolor{PastelRed}{HTML}{8F0D0D}")
    a(r"\definecolor{GoldenEarth}{HTML}{E7D192}")
    a(r"\colorlet{name}{black}")
    a(r"\colorlet{tagline}{PastelRed}")
    a(r"\colorlet{heading}{DarkPastelRed}")
    a(r"\colorlet{headingrule}{GoldenEarth}")
    a(r"\colorlet{subheading}{PastelRed}")
    a(r"\colorlet{accent}{PastelRed}")
    a(r"\colorlet{emphasis}{SlateGrey}")
    a(r"\colorlet{body}{LightGrey}")
    a("")

    full_name = escape_latex(pi.name["first"]) + " " + escape_latex(pi.name["family"])
    a(r"\name{{{}}}".format(full_name))
    a(r"\tagline{{{}}}".format(pi.title))

    info_items = []
    if pi.email:
        clean_email, display_email = email_parts(pi.email)
        info_items.append(r"\printinfo[email]{\faAt}{%s}[mailto:%s]" % (display_email, clean_email))
    if pi.phone:
        info_items.append(r"\phone{{{}}}".format(obfuscate_phone(pi.phone)))
    if pi.address:
        info_items.append(r"\location{{{}}}".format(escape_latex(pi.address)))
    if pi.github:
        gh_user = pi.github.rstrip("/").split("/")[-1]
        info_items.append(r"\github{{{}}}".format(gh_user))
    if pi.linkedin:
        li_user = pi.linkedin.rstrip("/").split("/")[-1]
        info_items.append(r"\linkedin{{{}}}".format(li_user))
    info_block = "%\n  ".join(info_items)
    a(r"\personalinfo{%")
    a(r"  {}".format(info_block))
    a(r"}")
    a("")
    a(r"\usepackage{qrcode}")
    a("")
    full_name = unescape_latex(pi.name["first"] + " " + pi.name["family"])
    raw_title = unescape_latex(pi.title)
    repo_url = pi.github.rstrip("/") + "/cvpoly"
    a(r"\hypersetup{")
    a(r"  pdfauthor={{{}}},".format(full_name))
    a(r"  pdftitle={{CV - {}}},".format(raw_title))
    a(r"  pdfsubject={{CV - {}}},".format(full_name))
    a(r"  pdfkeywords={{CV, {}}}".format(repo_url))
    a(r"}")
    a("")

    a(r"\begin{document}")
    a(r"\makecvheader")
    a("")

    a(r"\begin{paracol}{2}")
    a("")

    # ── LEFT COLUMN: Expériences ──
    a(r"\cvsection{Expériences}")
    for i, exp in enumerate(data.experience):
        if i > 0:
            a(r"\divider")
        dates = format_date_range(exp.dates.start, exp.dates.end)
        duration = compute_duration(exp.dates.start, exp.dates.end)
        dates_label = f"{dates} ({duration})" if duration else dates
        a(r"\cvevent{{{}}}{{{}}}{{{}}}{{}}".format(
            escape_latex(exp.role),
            escape_latex(exp.company),
            dates_label,
        ))
        a("  {}".format(exp.summary))
        if exp.stack:
            a(r"  \\ {{\small\textbf{{Stack :}} {}}}".format(
                ", ".join(exp.stack)
            ))
        a("")
    a("")

    # ── RIGHT COLUMN ──
    a(r"\switchcolumn")
    a("")

    # Compétences
    a(r"\cvsection{Compétences}")
    for cat in data.skills:
        a(r"\cvsubsection{{{}}}".format(cat.name))
        tags = " ".join(r"\cvtag{{{}}}".format(item) for item in cat.items)
        a(r"  {}\par".format(tags))
    a("")


    # Formations professionnelles
    if data.professional_education:
        a(r"\cvsection{Formations professionnelles}")
        for pe in data.professional_education:
            dates = ""
            if pe.dates:
                dates = format_date_range(pe.dates.start, pe.dates.end)
            loc = pe.location if pe.location else ""
            a(r"\cvevent{{{}}}{{{}}}{{{}}}{{{}}}".format(
                escape_latex(pe.course),
                escape_latex(pe.organization),
                dates,
                escape_latex(loc),
            ))
            a("")
        a("")
    a("")

    # Formation initiale
    a(r"\cvsection{Formation initiale}")
    for edu in data.initial_education:
        dates = ""
        if edu.dates:
            dates = format_date_range(edu.dates.start, edu.dates.end)
        loc = edu.location if edu.location else ""
        a(r"\cvevent{{{}}}{{{}}}{{{}}}{{{}}}".format(
            escape_latex(edu.degree),
            escape_latex(edu.school),
            dates,
            escape_latex(loc),
        ))
        if edu.details:
            a(r"  {}".format(edu.details))
        a("")

    # Langues
    if data.languages:
        a(r"\cvsection{Langues}")
        for lg in data.languages:
            a(r"  {}\par".format(r"\cvtag{{{}}}".format(lg.language)))
            parts = lg.level.split(" -- ")
            for p in parts:
                a(r"  {}\par".format(r"\cvtag{{{}}}".format(p.strip())))
        a("")

    # ── QR Code ──
    a(r"\cvsection{Références}")
    a(r"\qrcode[height=2cm]{" + repo_url + r"}\par")
    a(r"{\small \url{" + repo_url + r"}}")
    a("")

    a(r"\end{paracol}")
    a(r"\end{document}")
    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        data = load_cv("cv.json")
        errors = validate_cv_data(data)
        if errors:
            for e in errors:
                print(f"[ERROR] {e}")
            sys.exit(1)
        else:
            print("[OK] Validation passed")
            return

    os.makedirs(BUILD_DIR, exist_ok=True)

    data = load_cv("cv.json")

    errors = validate_cv_data(data)
    for e in errors:
        print(f"[WARN] {e}")

    moderncv_tex = render_moderncv(data)
    altacv_tex = render_altacv(data)

    with open(os.path.join(BUILD_DIR, "cv_moderncv.tex"), "w", encoding="utf-8") as f:
        f.write(moderncv_tex)
    print("[OK] build/cv_moderncv.tex")

    with open(os.path.join(BUILD_DIR, "cv_altacv.tex"), "w", encoding="utf-8") as f:
        f.write(altacv_tex)
    print("[OK] build/cv_altacv.tex")


if __name__ == "__main__":
    main()
