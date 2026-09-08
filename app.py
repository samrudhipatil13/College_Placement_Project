import base64
import os
import streamlit as st
import streamlit.components.v1 as components
from contextlib import contextmanager
from utils.auth_utils import register_user, generate_otp, verify_otp, get_user_by_email, login_user

try:
    from database.db_connection import get_connection
except Exception:
    get_connection = None

# ---------------- BRANDING CONFIG — update these once you have final assets ----------------
COLLEGE_NAME = "D. Y. Patil Technical Campus, Talsande"
LOGO_URL = "https://dypgroup.edu.in/wp-content/uploads/2020/01/logo.jpg"
HERO_IMAGE_PATH = "assets/campus-front.png"
HERO_IMAGE_FALLBACK_URL = "https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/front-view.png"

# Controls which PART of the hero photo stays visible after cropping to fit
# the banner (since the photo's shape rarely matches the banner's shape).
# Format: "horizontal vertical" — each can be: left/center/right (or a %)
# for horizontal, and top/center/bottom (or a %) for vertical.
# Examples:
#   "center center"  -> default, crops equally from all sides
#   "center top"     -> keeps the TOP of the photo visible (crops from bottom) — good for building signage/name boards
#   "center bottom"  -> keeps the BOTTOM visible (crops from top)
#   "30% 20%"        -> keeps the area 30% from the left, 20% from the top
HERO_IMAGE_POSITION = "center 30%"

# ---------------- SESSION STATE ----------------
if "stage" not in st.session_state:
    st.session_state.stage = "home"
if "pending_user_id" not in st.session_state:
    st.session_state.pending_user_id = None
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

NAV_STAGES = ["home", "about", "facilities", "register", "login"]

# Always use wide layout so the navbar never has to squeeze/wrap;
# form pages are centered manually using columns instead.
st.set_page_config(
    page_title="DYPTC Talsande | Placement Cell",
    layout="wide",
    page_icon="🎓",
)


@contextmanager
def centered(ratio=(1, 2, 1)):
    """Render content in the middle column so form pages still look centered
    even though the overall page layout is wide (needed for the navbar)."""
    left, mid, right = st.columns(ratio)
    with mid:
        yield


def local_image_uri(path, fallback_url=""):
    """Reads an image from the local project folder and returns it as a
    data: URI, so it can be dropped straight into an <img src="..."> tag
    with no external hosting required. Falls back to fallback_url if the
    file isn't found yet."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        mime = "jpeg" if ext == "jpg" else (ext or "png")
        b64 = base64.b64encode(data).decode()
        return f"data:image/{mime};base64,{b64}"
    except Exception:
        return fallback_url


def _text_logo_data_uri(text):
    """Builds a simple text logo as an inline SVG (used only if LOGO_URL is empty)."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="260" height="44">
        <text x="0" y="30" font-family="Arial, sans-serif" font-size="24"
              font-weight="800" fill="#1a2a4a">🎓 {text}</text>
    </svg>"""
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


def apply_theme(college_name=COLLEGE_NAME, logo_url=LOGO_URL):
    st.markdown("""
    <style>
        /* Tells browsers (incl. Chrome's "Force dark mode for web contents")
           that this page is deliberately light-themed, so they don't invert
           our colors and turn text invisible. */
        :root, .stApp { color-scheme: only light; }

        /* Hard-force dark, readable text on the SPECIFIC elements that a
           phone's forced-dark mode was flipping to invisible white-on-white:
           widget labels (Email/Password), radio option text (Register/Login),
           and section headers (Login/Student Registration/etc). These
           selectors only ever appear on our white cards, never on the dark
           hero/footer/sidebar, so this is safe to force everywhere. */
        h2, h3,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        div[role="radiogroup"] label p,
        div[role="radiogroup"] label span,
        [data-testid="stCaptionContainer"] p,
        .stCaption {
            color: #1a2a4a !important;
        }

        /* ---- Page background: soft gradient over a faded campus photo ---- */
        .stApp {
            background:
                linear-gradient(180deg, rgba(244,247,251,0.93) 0%, rgba(238,242,247,0.96) 100%),
                url('https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/college-view.png')
                no-repeat center center fixed;
            background-size: cover;
        }

        .block-container { padding-top: 4rem; padding-bottom: 3rem; }

        h1, h2, h3 { color: #1a2a4a; }

        /* ---- Navbar (landing pages) ---- */
        .navbar {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.6rem 1rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 2px 10px rgba(26, 42, 74, 0.05);
        }
        .brand {
            font-size: 1.15rem;
            font-weight: 800;
            color: #1a2a4a;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            height: 100%;
        }
        .brand img { height: 40px; width: auto; border-radius: 4px; }
        .navbar .stButton > button {
            background-color: transparent;
            color: #33415c;
            border: none;
            font-weight: 600;
            padding: 0.45rem 0.9rem;
            box-shadow: none;
            white-space: nowrap;
            min-width: max-content;
        }
        .navbar .stButton > button:hover {
            background-color: #eef2f7;
            color: #1a2a4a;
        }

        /* ---- Stat / Feature / Facility cards ---- */
        .card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.4rem 1.2rem;
            text-align: center;
            box-shadow: 0 4px 14px rgba(26, 42, 74, 0.05);
            height: 100%;
        }
        .card h3 { margin-bottom: 0.2rem; font-size: 1.6rem; color: #2f4a7c; word-break: break-word; }
        .card p { margin: 0; color: #64748b; font-size: 0.92rem; }

        .feature-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.5rem;
            height: 100%;
            box-shadow: 0 4px 14px rgba(26, 42, 74, 0.05);
        }
        .feature-card .icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
        .feature-card h4 { color: #1a2a4a; margin-bottom: 0.35rem; }
        .feature-card p { color: #64748b; font-size: 0.92rem; margin: 0; }

        /* ---- Forms, tables & widgets ---- */
        div[data-testid="stForm"] {
            background-color: #ffffff;
            padding: 2rem 2rem 1rem 2rem;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 14px rgba(26, 42, 74, 0.06);
        }
        input, textarea, select { border-radius: 8px !important; }

        div[data-testid="stDataFrame"], div[data-testid="stTable"] {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 0.4rem;
        }

        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1rem;
            box-shadow: 0 4px 14px rgba(26, 42, 74, 0.05);
        }

        .stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background-color: #1a2a4a;
            color: #ffffff;
            border-radius: 8px;
            border: none;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            width: 100%;
            transition: background-color 0.2s ease-in-out;
        }
        .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #2f4a7c;
            color: #ffffff;
        }

        div[data-testid="stAlert"] { border-radius: 10px; }

        /* ---- Sidebar (multipage nav) ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #10192f 0%, #1a2a4a 100%);
            border-right: none;
        }
        section[data-testid="stSidebar"] * { color: #dbe4f5 !important; }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] { padding-top: 0.6rem; }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
            border-radius: 8px;
            margin: 0.15rem 0.7rem;
            padding: 0.55rem 0.9rem !important;
            transition: background-color 0.15s ease, padding-left 0.15s ease;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
            background-color: rgba(255,255,255,0.10);
            padding-left: 1.1rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
            background-color: #2f4a7c;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12); }

        .sidebar-brand {
            font-size: 1.15rem;
            font-weight: 800;
            color: #ffffff !important;
            padding: 0.4rem 1rem 1rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            margin-bottom: 0.4rem;
        }

        footer, #MainMenu { visibility: hidden; }
        .app-footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.82rem;
            margin-top: 2.5rem;
        }

        /* ---- Image hero ---- */
        .img-hero {
            position: relative;
            border-radius: 18px;
            overflow: hidden;
            margin-bottom: 1.2rem;
            height: 380px;
        }
        .img-hero img { width: 100%; height: 100%; object-fit: cover; display: block; }
        /* object-position for the hero photo is set inline per-image via HERO_IMAGE_POSITION,
           so it can be tuned without touching this stylesheet. */
        .img-hero::after {
            content: "";
            position: absolute; inset: 0;
            background: linear-gradient(180deg, rgba(10,18,38,0.15) 0%, rgba(10,18,38,0.85) 100%);
        }
        .img-hero .hero-text {
            position: absolute; left: 2rem; bottom: 2rem; right: 2rem; z-index: 2;
            color: #ffffff;
        }
        .img-hero .hero-text .tag {
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 0.25rem 0.8rem;
            border-radius: 999px;
            font-size: 0.8rem;
            display: inline-block;
            margin-bottom: 0.6rem;
        }
        .img-hero .hero-text h1 { color: #ffffff; font-size: 2.2rem; margin: 0 0 0.4rem 0; }
        .img-hero .hero-text p { color: #dbe4f5; max-width: 560px; margin: 0; font-size: 0.98rem; }
        .hero-badge {
            position: absolute; z-index: 3; right: 2rem; top: -1.4rem;
            background: #ffffff; color: #1a2a4a;
            border-radius: 12px; padding: 0.8rem 1.2rem;
            box-shadow: 0 8px 22px rgba(26,42,74,0.18);
            text-align: center;
        }
        .hero-badge .num { font-size: 1.3rem; font-weight: 800; color: #2f4a7c; display: block; }
        .hero-badge .lbl { font-size: 0.72rem; color: #64748b; }

        /* ---- Infrastructure grid ---- */
        .infra-item { position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 0.9rem; height: 170px; }
        .infra-item img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }
        .infra-item:hover img { transform: scale(1.06); }
        .infra-item .cap {
            position: absolute; left: 0; right: 0; bottom: 0;
            background: linear-gradient(0deg, rgba(10,18,38,0.85), rgba(10,18,38,0));
            color: #fff; padding: 0.7rem 0.8rem 0.5rem; font-weight: 600; font-size: 0.88rem;
        }

        /* ---- Site footer ---- */
        .site-footer {
            background-color: #10192f;
            color: #b7c2da;
            border-radius: 18px;
            padding: 2.5rem 2.5rem 1.2rem;
            margin-top: 3rem;
        }
        .site-footer h5 { color: #ffffff; font-size: 0.95rem; margin-bottom: 0.8rem; }
        .site-footer p, .site-footer a { color: #b7c2da; font-size: 0.86rem; text-decoration: none; line-height: 2; }
        .site-footer a:hover { color: #ffffff; }
        .site-footer .bottom-line {
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 1.5rem; padding-top: 1rem;
            font-size: 0.78rem; color: #7d8bab; text-align: center;
        }

        /* ---- Mobile responsiveness ---- */
        @media (max-width: 768px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 5rem; }

            .navbar { text-align: center; }
            .navbar .brand { justify-content: center; margin-bottom: 0.5rem; font-size: 1.15rem; }
            .navbar .stButton > button { font-size: 0.85rem; padding: 0.4rem 0.5rem; }

            .img-hero { height: 300px; }
            .img-hero .hero-text { left: 1.2rem; right: 1.2rem; bottom: 1.2rem; }
            .img-hero .hero-text h1 { font-size: 1.5rem; }
            .img-hero .hero-text p { font-size: 0.85rem; }
            .hero-badge { top: unset; bottom: -1.2rem; right: 1rem; padding: 0.6rem 0.9rem; }
            .hero-badge .num { font-size: 1.05rem; }

            .card h3 { font-size: 1.3rem; }
            .feature-card, .card { padding: 1.1rem; }

            .infra-item { height: 130px; }

            .site-footer { padding: 1.8rem 1.4rem 1rem; }
        }
    </style>
    """, unsafe_allow_html=True)

    try:
        st.logo(logo_url or _text_logo_data_uri(college_name))
    except Exception:
        pass  # st.logo needs Streamlit >= 1.30; safe to skip on older versions

    # Extra, stronger signal against phone browsers that force-invert colors
    # ("Force dark mode for web contents"): add a real <meta name="color-scheme">
    # tag straight into the actual page <head>, which is what browsers check.
    components.html("""
    <script>
        try {
            var doc = window.parent.document;
            if (!doc.querySelector('meta[name="color-scheme"]')) {
                var meta = doc.createElement('meta');
                meta.name = 'color-scheme';
                meta.content = 'light';
                doc.head.appendChild(meta);
            }
            doc.documentElement.style.colorScheme = 'light';
        } catch (e) {}
    </script>
    """, height=0, width=0)


@st.cache_data(ttl=15)
def get_live_stats():
    """Real counts straight from the database. Each stat fails independently —
    a table that doesn't exist yet (e.g. companies/drives before those modules
    are built) shows 'Coming soon' instead of breaking the page. If the DB
    itself is unreachable, everything falls back to 'N/A'."""
    stats = {"students": "N/A", "companies": "N/A", "drives": "N/A", "applications": "N/A"}
    if get_connection is None:
        return stats
    try:
        conn = get_connection()
    except Exception:
        return stats

    queries = {
        "students": "SELECT COUNT(*) FROM users WHERE role = 'student'",
        "companies": "SELECT COUNT(*) FROM companies",
        "drives": "SELECT COUNT(*) FROM drives",
        "applications": "SELECT COUNT(*) FROM applications",
    }
    for key, sql in queries.items():
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            stats[key] = cursor.fetchone()[0]
            cursor.close()
        except Exception:
            stats[key] = "Coming soon"  # table not built yet
    try:
        conn.close()
    except Exception:
        pass
    return stats


# ---------------- APPLY SHARED THEME ----------------
apply_theme()



# ---------------- NAVBAR ----------------
def render_navbar():
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    c_brand, c1, c2, c3, c4 = st.columns([2.6, 0.9, 0.9, 1.1, 1.5])
    with c_brand:
        st.markdown(
            '<div class="brand">'
            '<img src="https://dypgroup.edu.in/wp-content/uploads/2020/01/logo.jpg" />'
            'DYPTC Talsande</div>',
            unsafe_allow_html=True,
        )
    with c1:
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.stage = "home"
            st.rerun()
    with c2:
        if st.button("About", key="nav_about", use_container_width=True):
            st.session_state.stage = "about"
            st.rerun()
    with c3:
        if st.button("Facilities", key="nav_facilities", use_container_width=True):
            st.session_state.stage = "facilities"
            st.rerun()
    with c4:
        if st.button("Login / Register", key="nav_login", use_container_width=True):
            st.session_state.stage = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


if st.session_state.stage in NAV_STAGES:
    render_navbar()

# =========================================================
# HOME
# =========================================================
if st.session_state.stage == "home":
    hero_img = local_image_uri(HERO_IMAGE_PATH, HERO_IMAGE_FALLBACK_URL)
    st.markdown(f"""
    <div class="img-hero">
        <img src="{hero_img}" style="object-position: {HERO_IMAGE_POSITION};" />
        <div class="hero-text">
            <h1>Student Placement Management &amp; Analytics System</h1>
            <p>One centralized platform for students and the TPO — manage profiles, discover
            eligible drives, apply in a click, and track every application in real time.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Get Started — Register Now", key="hero_cta"):
        st.session_state.stage = "register"
        st.rerun()

    st.write("")
    live = get_live_stats()
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        (live["students"], "Students Registered"),
        (live["companies"], "Partner Companies"),
        (live["drives"], "Active Drives"),
        (live["applications"], "Applications Submitted"),
    ]
    for col, (num, label) in zip([s1, s2, s3, s4], stats):
        size_class = "" if isinstance(num, int) else ' style="font-size:1.1rem;"'
        with col:
            st.markdown(f'<div class="card"><h3{size_class}>{num}</h3><p>{label}</p></div>', unsafe_allow_html=True)

    st.write("")
    st.subheader("Why students & TPOs choose us")
    f1, f2, f3 = st.columns(3)
    features = [
        ("🎯", "Dynamic Eligibility", "Instantly know which drives you qualify for, with a clear reason when you don't."),
        ("📄", "One-Click Applications", "Apply to eligible drives in seconds and track status from a single dashboard."),
        ("📊", "TPO Analytics & Export", "Admins get a live dashboard and can export applicant data to Excel instantly."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.subheader("Campus Infrastructure")
    infra_images = [
        ("https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/central-library.png", "Central Library"),
        ("https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/rnd.png", "Research Labs"),
        ("https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/gymkhana.png", "Sports Complex"),
        ("https://pub-853e5048ad6b439d9d1101d981160323.r2.dev/campus/yoga-center.png", "Campus Yoga Center"),
    ]
    ic1, ic2, ic3, ic4 = st.columns(4)
    for col, (img, cap) in zip([ic1, ic2, ic3, ic4], infra_images):
        with col:
            st.markdown(f"""
            <div class="infra-item">
                <img src="{img}" />
                <div class="cap">{cap}</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("Explore All Facilities", key="explore_facilities"):
        st.session_state.stage = "facilities"
        st.rerun()

    # ---- Footer ----
    st.markdown("""
    <div class="site-footer">
        <div style="display:flex; flex-wrap:wrap; gap:2.5rem; justify-content:space-between;">
            <div style="flex:1; min-width:220px;">
                <h5>🎓 D.Y. Patil Technical Campus, Talsande</h5>
                <p>Wathar-Warananagar Road, Talsande<br/>Tal. Hatkanagale, Dist. Kolhapur – 416112</p>
                <p>foet.dypgroup.edu.in</p>
            </div>
            <div style="flex:1; min-width:180px;">
                <h5>About</h5>
                <p>About the Platform<br/>Vision &amp; Mission<br/>Facilities<br/>Contact Us</p>
            </div>
            <div style="flex:1; min-width:180px;">
                <h5>For Students</h5>
                <p>Register<br/>Login<br/>My Applications<br/>Eligibility Check</p>
            </div>
            <div style="flex:1; min-width:180px;">
                <h5>Placements &amp; Career</h5>
                <p>Partner Companies<br/>Active Drives<br/>Placement Records<br/>Alumni</p>
            </div>
        </div>
        <div class="bottom-line">© 2026 D.Y. Patil Technical Campus, Talsande — Placement Cell · Built for students, by students</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ABOUT
# =========================================================
elif st.session_state.stage == "about":
    st.header("About D.Y. Patil Technical Campus, Talsande")
    st.write("""
    This is the official placement management platform of D.Y. Patil Technical
    Campus, Talsande, built to bring students and the Training & Placement Office
    (TPO) onto one simple, transparent system.
    """)

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Our Mission</h4>
            <p>To make campus placements transparent and efficient — every student
            should know exactly where they stand and why, without chasing the
            placement office for updates.</p>
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown("""
        <div class="feature-card">
            <h4>🌱 Our Vision</h4>
            <p>A single digital record of every student's placement journey — from
            registration to offer letter — that grows smarter with analytics
            every year.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.subheader("What the platform does today")
    st.markdown("""
    - Secure student registration with OTP-based account verification
    - Rich student profiles — academics, skills, certifications, resume
    - A searchable directory of companies and placement drives
    - An automatic eligibility engine that explains eligible/not-eligible results
    - A TPO dashboard to manage drives, applicants, and export reports to Excel
    """)

    st.info("📌 Attendance tracking, recruitment rounds, notifications, and Power BI analytics are planned for Phase 2.")

# =========================================================
# FACILITIES
# =========================================================
elif st.session_state.stage == "facilities":
    st.header("Facilities")
    st.write("Everything students and the placement office need, in one place.")

    facilities = [
        ("🔐", "Secure Authentication", "Password hashing with bcrypt plus OTP verification keeps every account safe."),
        ("🧑‍🎓", "Student Profiles", "Maintain academic details, skills, certifications, projects, and resume in one profile."),
        ("🏢", "Company Directory", "Browse every partner company along with role, package, and drive details."),
        ("🎯", "Dynamic Eligibility Check", "Automatically compares your profile against each drive's criteria and explains the result."),
        ("📝", "Easy Applications", "Apply to eligible drives in one click, with duplicate and deadline protection built in."),
        ("📈", "TPO Dashboard", "Admins get a live overview — total students, companies, drives, and applications."),
        ("📤", "Excel Export", "TPOs can export applicant lists per drive to a ready-to-use .xlsx file."),
        ("📌", "Application Tracking", "Students can track every application's status from submission to result."),
    ]

    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(facilities):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="feature-card" style="margin-bottom: 1rem;">
                <div class="icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# REGISTRATION
# =========================================================
elif st.session_state.stage == "register":
    with centered():
        choice = st.radio("Choose an option:", ["Register", "Login"], index=0, horizontal=True)
        if choice == "Login":
            st.session_state.stage = "login"
            st.rerun()

        st.header("Student Registration")

        with st.form("registration_form"):
            email = st.text_input("College/Gmail Email")
            password = st.text_input("Create Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success, message = register_user(email, password, role="student")
                    if success:
                        user = get_user_by_email(email)
                        otp = generate_otp(user['user_id'])
                        st.session_state.pending_user_id = user['user_id']
                        st.session_state.generated_otp = otp
                        st.session_state.stage = "verify_otp"
                        st.rerun()
                    else:
                        st.error(message)

# =========================================================
# OTP VERIFICATION
# =========================================================
elif st.session_state.stage == "verify_otp":
    with centered():
        st.header("Verify Your Account")
        st.info(f"📧 (Simulated email) Your OTP is: **{st.session_state.generated_otp}**")
        st.caption("In the final version, this will be emailed to you instead of shown here.")

        entered_otp = st.text_input("Enter the 6-digit OTP")
        if st.button("Verify"):
            success, message = verify_otp(st.session_state.pending_user_id, entered_otp)
            if success:
                st.success(message)
                st.session_state.stage = "login"
                st.rerun()
            else:
                st.error(message)

# =========================================================
# LOGIN
# =========================================================
elif st.session_state.stage == "login":
    with centered():
        choice = st.radio("Choose an option:", ["Register", "Login"], index=1, horizontal=True)
        if choice == "Register":
            st.session_state.stage = "register"
            st.rerun()

        st.header("Login")

        with st.form("login_form"):
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")

            if login_submitted:
                success, user, message = login_user(login_email, login_password)
                if success:
                    st.session_state.logged_in_user = user
                    st.session_state.stage = "dashboard"
                    st.rerun()
                else:
                    st.error(message)

# =========================================================
# DASHBOARD
# =========================================================
elif st.session_state.stage == "dashboard":
    with centered():
        user = st.session_state.logged_in_user

        if user['role'] == 'admin':
            st.success(f"🎉 Welcome, TPO Admin ({user['email']})!")
            st.info("Use the sidebar to navigate to the TPO Dashboard.")
        else:
            st.success(f"🎉 Welcome, {user['email']}!")
            st.info("Use the sidebar to navigate to your Student Profile.")

        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.session_state.stage = "home"
            st.rerun()