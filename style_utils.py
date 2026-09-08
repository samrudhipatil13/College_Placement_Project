"""
Shared visual theme for the whole placement portal.

USAGE — add these two lines at the very top of EVERY page file
(app.py, pages/1_Student_Profile.py, pages/2_TPO_Dashboard.py, etc.),
right after st.set_page_config(...):

    from style_utils import apply_theme
    apply_theme()

That's it — background, cards, buttons, forms, tables, and the sidebar
will all match across every module without copy-pasting CSS into each file.

Once you have your real college name and a logo image, update the two
CONFIG values below (COLLEGE_NAME, LOGO_URL) — every page updates
automatically, nothing else needs to change.
"""

import base64
import streamlit as st

# ---------------- CONFIG — update these once you have real branding ----------------
COLLEGE_NAME = "D. Y. Patil Technical Campus, Talsande"
LOGO_URL = "https://dypgroup.edu.in/wp-content/uploads/2020/01/logo.jpg"


def _text_logo_data_uri(text):
    """Builds a simple text logo as an inline SVG (no external image needed yet).
    Once LOGO_URL is set to a real image, this is skipped entirely."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="260" height="44">
        <text x="0" y="30" font-family="Arial, sans-serif" font-size="24"
              font-weight="800" fill="#1a2a4a">🎓 {text}</text>
    </svg>"""
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


def apply_theme(college_name=COLLEGE_NAME, logo_url=LOGO_URL):
    st.markdown("""
    <style>
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

        /* ---- Stat / Feature / Facility cards — usable on any page ---- */
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

        /* ---- Forms, tables & widgets — applies on every page ---- */
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

        /* ---- Sidebar (multipage nav: Student Profile, TPO Dashboard, etc.) ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #10192f 0%, #1a2a4a 100%);
            border-right: none;
        }
        section[data-testid="stSidebar"] * { color: #dbe4f5 !important; }

        /* Native multipage nav links */
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

        /* ---- Image hero (landing page) ---- */
        .img-hero {
            position: relative;
            border-radius: 18px;
            overflow: hidden;
            margin-bottom: 1.2rem;
            height: 380px;
        }
        .img-hero img { width: 100%; height: 100%; object-fit: cover; display: block; }
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

        /* ---- Infrastructure grid (landing page) ---- */
        .infra-item { position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 0.9rem; height: 170px; }
        .infra-item img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }
        .infra-item:hover img { transform: scale(1.06); }
        .infra-item .cap {
            position: absolute; left: 0; right: 0; bottom: 0;
            background: linear-gradient(0deg, rgba(10,18,38,0.85), rgba(10,18,38,0));
            color: #fff; padding: 0.7rem 0.8rem 0.5rem; font-weight: 600; font-size: 0.88rem;
        }

        /* ---- Site footer (landing page) ---- */
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

    # ---- Sidebar branding: logo/name shown above the page nav on every page ----
    try:
        st.logo(logo_url or _text_logo_data_uri(college_name))
    except Exception:
        pass  # st.logo needs Streamlit >= 1.30; safe to skip on older versions