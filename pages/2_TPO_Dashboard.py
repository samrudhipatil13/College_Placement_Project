import html
import streamlit as st
from database.db_connection import get_connection

st.set_page_config(page_title="TPO Dashboard", page_icon="📊", layout="wide")

# ---------------- Guard: only logged-in admins ----------------
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user["role"] != "admin":
    st.warning("This page is for TPO/Admin only.")
    st.stop()

# ---------------- Theme (fixed colours, same in light & dark system mode) ----------------
BG = "#0a1128"
CARD = "#0f1b3d"
BORDER = "#1e2d5a"
MUTED = "#94a3b8"

# Page is declared a dark colour-scheme and every colour is explicit, so the
# browser / OS dark mode has nothing left to invert.
st.markdown(
    f"""
<style>
:root, html, body, .stApp {{ color-scheme: dark !important; }}
.stApp, [data-testid="stMain"], [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
}}
[data-testid="stMain"] .block-container {{ padding-top: 4rem; max-width: 1200px; }}
[data-testid="stHeader"] {{ background: transparent !important; }}

.hdr {{
    background: linear-gradient(135deg, #1a2a6c 0%, #0f1b3d 100%) !important;
    border: 1px solid {BORDER}; border-radius: 16px;
    padding: 24px 28px; margin-bottom: 22px;
}}
.hdr-title {{ color: #ffffff !important; font-size: 1.7rem; font-weight: 700; margin: 0; }}
.hdr-sub   {{ color: {MUTED} !important; font-size: .95rem; margin-top: 6px; }}

.kpi-grid {{
    display: grid; gap: 16px;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
}}
.kpi {{
    background: {CARD} !important; border: 1px solid {BORDER};
    border-radius: 14px; padding: 18px 20px;
}}
.kpi-top {{ display: flex; justify-content: space-between; align-items: center; }}
.kpi-lbl {{ color: {MUTED} !important; font-size: .85rem; font-weight: 600; }}
.kpi-ic  {{ font-size: 1.3rem; }}
.kpi-num {{ font-size: 2.1rem; font-weight: 800; margin: 8px 0 2px; line-height: 1.1; }}
.kpi-sub {{ color: {MUTED} !important; font-size: .8rem; }}
</style>
""",
    unsafe_allow_html=True,
)


def scalar(cursor, query, default=0):
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else default
    except Exception:
        return default


conn = get_connection()
total_students = total_companies = total_drives = active_drives = 0
total_applications = students_applied = 0
avg_cgpa = 0.0

if conn is not None:
    cur = conn.cursor()
    total_students = scalar(cur, "SELECT COUNT(*) FROM students")
    total_companies = scalar(cur, "SELECT COUNT(*) FROM companies")
    total_drives = scalar(cur, "SELECT COUNT(*) FROM drives")
    active_drives = scalar(cur, "SELECT COUNT(*) FROM drives WHERE drive_status = 'active'")
    total_applications = scalar(cur, "SELECT COUNT(*) FROM applications")
    students_applied = scalar(cur, "SELECT COUNT(DISTINCT student_id) FROM applications")
    avg_cgpa = float(scalar(cur, "SELECT AVG(cgpa) FROM students", 0.0))
    cur.close()
    conn.close()

pct = (students_applied / total_students * 100) if total_students else 0
per_student = (total_applications / total_students) if total_students else 0

who = html.escape(str(user.get("email", "")))
st.markdown(
    f"""
<div class="hdr">
  <div class="hdr-title" style="color:#ffffff;">📊 Placement Analytics</div>
  <div class="hdr-sub" style="color:{MUTED};">Training &amp; Placement Cell · Signed in as {who}</div>
</div>
""",
    unsafe_allow_html=True,
)

kpis = [
    ("Total Students", "🎓", "#38bdf8", f"{total_students}", f"{students_applied} have applied ({pct:.0f}%)"),
    ("Partner Companies", "🏢", "#34d399", f"{total_companies}", "Registered companies"),
    ("Active Drives", "🚀", "#fb923c", f"{active_drives}", f"of {total_drives} total drives"),
    ("Applications", "📝", "#f472b6", f"{total_applications}", f"{per_student:.1f} per student"),
    ("Avg CGPA", "📈", "#818cf8", f"{avg_cgpa:.2f}", "Across all students"),
]

cards = "".join(
    f'<div class="kpi" style="background:{CARD};">'
    f'<div class="kpi-top"><span class="kpi-lbl" style="color:{MUTED};">{lbl}</span>'
    f'<span class="kpi-ic">{icon}</span></div>'
    f'<div class="kpi-num" style="color:{color};">{num}</div>'
    f'<div class="kpi-sub" style="color:{MUTED};">{sub}</div></div>'
    for lbl, icon, color, num, sub in kpis
)
st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)

# Phase 2: charts, analytics tabs, recent applications, quick actions.