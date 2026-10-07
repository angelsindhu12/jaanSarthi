import streamlit as st
import io
import json
import re
from datetime import datetime

# Local modules
from app.core.i18n import LANGUAGES, t
from app.services.auth_service import AuthService
from app.ml.data_loader import DatasetLoader
from app.ml.matcher import EligibilityMatcher
from app.ml.rag_engine import MultilingualRAGEngine
from app.services.ocr_service import DocumentOCRService
from app.services.document_analyzer import DocumentAnalyzer

st.set_page_config(
    page_title="National Digital Scheme & Employment Portal | भारत सरकार",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CONSTANTS & VALIDATION HELPERS -----------------
GENDER_OPTIONS = ["Male", "Female", "Others"]

ALL_INDIAN_STATES = [
    "All India",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi (NCT)",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry"
]

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def is_valid_email(email_str: str) -> bool:
    if not email_str:
        return False
    return bool(re.match(EMAIL_REGEX, email_str.strip()))

# ----------------- PROFESSIONAL GOVERNMENT VISUAL SYSTEM CSS -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    /* 1. Global Background & Crisp High-Contrast Typography */
    html, body, .stApp {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* 2. Streamlit Header Bar */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    
    /* 3. Official Public Service Sidebar */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        background: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* 4. Text and Labels - Accessible Slate Contrast */
    .stMarkdown p, .stMarkdown label, .stMarkdown span,
    p, label, .stCaption {
        color: #334155 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    /* 5. SELECTBOXES & DROPDOWNS */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="select"]:hover,
    div[data-baseweb="select"]:focus-within {
        border-color: #1E3A8A !important;
        box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.12) !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    div[data-baseweb="select"] svg {
        fill: #1E3A8A !important;
    }

    /* Dropdown Popover Menu */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="menu"],
    div[data-baseweb="menu"] *,
    ul[role="listbox"],
    [role="listbox"],
    [data-baseweb="popover"] [role="listbox"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
    }
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.06) !important;
        padding: 4px !important;
    }

    div[data-baseweb="popover"] li,
    ul[role="listbox"] li,
    li[role="option"],
    [role="option"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 6px !important;
        margin: 2px 0 !important;
        padding: 9px 12px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    div[data-baseweb="popover"] li *,
    ul[role="listbox"] li *,
    li[role="option"] *,
    [role="option"] * {
        color: #0F172A !important;
        background-color: transparent !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"],
    ul[role="listbox"] li:hover,
    ul[role="listbox"] li[aria-selected="true"],
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background-color: #EFF6FF !important;
        background: #EFF6FF !important;
        color: #1E40AF !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] li[aria-selected="true"] *,
    ul[role="listbox"] li:hover *,
    ul[role="listbox"] li[aria-selected="true"] *,
    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] * {
        color: #1E40AF !important;
        font-weight: 700 !important;
        background-color: transparent !important;
    }

    /* 6. Inputs (Text, Password, Number, Date) */
    [data-baseweb="input"],
    [data-baseweb="base-input"],
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stNumberInputRootElement"],
    div[data-testid="stDateInput"] > div {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    [data-baseweb="input"]:focus-within,
    [data-baseweb="base-input"]:focus-within,
    div[data-testid="stTextInputRootElement"]:focus-within {
        border-color: #1E3A8A !important;
        box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.15) !important;
    }
    input, textarea,
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
        caret-color: #1E3A8A !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        border: none !important;
    }
    input::placeholder,
    textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
        font-weight: 400 !important;
    }

    /* 7. Government Primary & Secondary Buttons */
    button,
    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="primary"],
    button[kind="secondary"],
    button[kind="primaryFormSubmit"],
    button[kind="secondaryFormSubmit"],
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primaryFormSubmit"],
    [data-testid="stBaseButton-secondaryFormSubmit"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 9px 20px !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.1px !important;
        box-shadow: 0 2px 6px rgba(30, 58, 138, 0.22) !important;
        cursor: pointer !important;
        transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button:hover,
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #172554 0%, #1E3A8A 100%) !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.32) !important;
        transform: translateY(-1px) !important;
    }
    button *,
    .stButton > button *,
    div[data-testid="stFormSubmitButton"] > button * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Official Portal External Link Buttons */
    [data-testid="stLinkButton"] a {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 18px !important;
        text-decoration: none !important;
        box-shadow: 0 2px 6px rgba(5, 150, 105, 0.2) !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        transition: all 0.18s ease !important;
    }
    [data-testid="stLinkButton"] a:hover {
        background: linear-gradient(135deg, #047857 0%, #065F46 100%) !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stLinkButton"] a * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* 8. Tabs Consistency & Active Navigation Bar */
    div[data-baseweb="tab-list"] {
        gap: 4px !important;
        border-bottom: 2px solid #E2E8F0 !important;
        padding-bottom: 0px !important;
        background: transparent !important;
    }
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 18px !important;
        background: transparent !important;
        transition: all 0.15s ease !important;
        border-bottom: 3px solid transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #1E3A8A !important;
        background-color: #F1F5F9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1E3A8A !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #1E3A8A !important;
        background: #F8FAFC !important;
    }

    /* 9. Standardized Government Card System */
    .gov-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    .gov-card:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
    }

    .gov-card-banner {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%) !important;
        border: 1.5px solid #BFDBFE !important;
        border-radius: 12px !important;
        padding: 20px 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.05) !important;
    }

    /* Left-Border Accent Cards */
    .card-scheme, .card-green {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #059669 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    .card-job, .card-blue, .card-navy {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #1E40AF !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    .card-tender, .card-amber {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #D97706 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    .card-deadline, .card-red {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #DC2626 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    .card-teal {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-left: 4px solid #0D9488 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }

    /* Standardized Trust and Verification Badges */
    .badge-gov {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 11.5px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        padding: 3px 9px;
        border-radius: 5px;
    }
    .badge-navy {
        background: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }
    .badge-green {
        background: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }
    .badge-amber {
        background: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    .badge-red {
        background: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .badge-teal {
        background: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
    }
    .badge-slate {
        background: #F1F5F9;
        color: #334155;
        border: 1px solid #CBD5E1;
    }

    /* 10. File Uploader Styling */
    [data-testid="stFileUploader"] {
        background-color: #F8FAFC !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 10px !important;
        padding: 16px !important;
        transition: border-color 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #1E3A8A !important;
    }

    /* 11. Subtle Process Step Bar */
    .process-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 16px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .process-step-item {
        font-size: 12.5px;
        font-weight: 600;
        color: #475569;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .process-arrow {
        color: #94A3B8;
        font-weight: 700;
    }

    /* 12. Search Box Prominence */
    .search-card-wrapper {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE SETUP -----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "cur_lang" not in st.session_state:
    st.session_state["cur_lang"] = "en"

# ----------------- SIDEBAR: OFFICIAL EMBLEM & CITIZEN PORTAL -----------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=58)
    st.markdown("### **🏛️ Citizen Service Portal**")
    st.caption("National Welfare Schemes, Public Notices & Employment Hub")
    
    # Language Switcher
    lang_names = list(LANGUAGES.values())
    curr_lang_idx = list(LANGUAGES.keys()).index(st.session_state["cur_lang"]) if st.session_state["cur_lang"] in LANGUAGES else 0
    sel_lang_name = st.selectbox(
        "🌐 Choose Language / भाषा चुनें",
        options=lang_names,
        index=curr_lang_idx
    )
    for code, name in LANGUAGES.items():
        if name == sel_lang_name:
            st.session_state["cur_lang"] = code
            break
            
    cur_lang = st.session_state["cur_lang"]
    st.divider()

    # User Status in Sidebar
    if st.session_state["logged_in"]:
        user = AuthService.get_user(st.session_state["user_email"])
        if user:
            user_sidebar_html = (
                f'<div style="background: #F8FAFC; border: 1.5px solid #BFDBFE; border-radius: 8px; padding: 12px; margin-bottom: 12px;">'
                f'<span style="color: #1E3A8A; font-weight: 700; font-size: 13.5px;">● {t("welcome_user", cur_lang)}, {user.get("name")}</span><br>'
                f'<span style="color: #475569; font-size: 12px;">{t("email", cur_lang)}: {user.get("email")}</span><br>'
                f'<span style="color: #475569; font-size: 12px;">{t("state", cur_lang)}: {user.get("profile", {}).get("state", "All India")}</span>'
                f'</div>'
            )
            st.markdown(user_sidebar_html, unsafe_allow_html=True)
            if st.button(t("logout_btn", cur_lang)):
                st.session_state["logged_in"] = False
                st.session_state["user_email"] = ""
                st.rerun()
    else:
        st.markdown(
            '<div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px;">'
            '<span style="color: #1E3A8A; font-weight: 700; font-size: 13px;">🛡️ Citizen Access Notice:</span><br>'
            '<span style="color: #475569; font-size: 12px; line-height: 1.5;">Please log in or register your citizen account to track applications, evaluate eligibility, and receive notification alerts.</span>'
            '</div>',
            unsafe_allow_html=True
        )

# Top National Tricolor Ribbon (Restrained Government Standard)
st.markdown('<div style="height: 4px; background: linear-gradient(90deg, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%); border-radius: 2px; margin-bottom: 16px;"></div>', unsafe_allow_html=True)

# Dignified National Government Portal Banner
banner_html = (
    f'<div class="gov-card-banner">'
    f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">'
    f'<div style="display: flex; align-items: center; gap: 16px;">'
    f'<div style="background: #FFFFFF; border: 1.5px solid #BFDBFE; width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 26px; box-shadow: 0 2px 6px rgba(30, 58, 138, 0.08);">'
    f'🏛️'
    f'</div>'
    f'<div>'
    f'<h2 style="color: #0F172A !important; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.3px;">'
    f'{t("app_title", cur_lang)}'
    f'</h2>'
    f'<p style="color: #475569 !important; margin: 4px 0 0 0; font-size: 13.5px; font-weight: 500;">'
    f'{t("app_subtitle", cur_lang)}'
    f'</p>'
    f'</div>'
    f'</div>'
    f'<div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">'
    f'<span class="badge-gov badge-green">🌿 100% Free Public Service</span>'
    f'<span class="badge-gov badge-navy">🇮🇳 Digital India Verified</span>'
    f'<span class="badge-gov badge-slate">🔒 Secure Citizen Gateway</span>'
    f'</div>'
    f'</div>'
    f'</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

# =========================================================================
# AUTHENTICATION SCREEN (LOGIN / REGISTER) - IF NOT LOGGED IN
# =========================================================================
if not st.session_state["logged_in"]:
    st.markdown(f"### 🔐 {t('login', cur_lang)} / {t('register', cur_lang)}")
    st.caption("Access official citizen services, personalized eligibility matching, and document explainer tools.")
    
    auth_tab1, auth_tab2 = st.tabs([
        f"🔑 {t('login', cur_lang)}",
        f"📝 {t('register', cur_lang)}"
    ])

    # Tab 1: Login Form
    with auth_tab1:
        st.markdown(
            '<div class="gov-card">'
            '<h4 style="margin-top:0; color:#1E3A8A;">Citizen Portal Login</h4>'
            '<p style="color:#64748B; font-size:13.5px; margin-bottom:14px;">Enter your registered citizen email and password to access your dashboard.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            login_email = st.text_input(t("email", cur_lang), placeholder="citizen@gmail.com")
            login_pass = st.text_input(t("password", cur_lang), type="password")
            btn_submit_login = st.form_submit_button(t("login_btn", cur_lang))

        if btn_submit_login:
            if not login_email or not login_pass:
                st.error("Please enter both email and password.")
            elif not is_valid_email(login_email):
                st.error("Please enter a valid email address (e.g. citizen@gmail.com).")
            else:
                res = AuthService.login(login_email, login_pass)
                if res["success"]:
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = login_email.strip().lower()
                    st.success("Login successful! Redirecting to Citizen Portal...")
                    st.rerun()
                else:
                    st.error(res["message"])

    # Tab 2: Register Form
    with auth_tab2:
        st.markdown(
            '<div class="gov-card">'
            '<h4 style="margin-top:0; color:#1E3A8A;">New Citizen Registration</h4>'
            '<p style="color:#64748B; font-size:13.5px; margin-bottom:14px;">Create your citizen profile to store applications, track exams, and receive personalized scheme & recruitment alerts.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        with st.form("register_form"):
            rc1, rc2 = st.columns(2)
            with rc1:
                reg_name = st.text_input(t("full_name", cur_lang), placeholder="Enter your full name")
                reg_email = st.text_input(t("email", cur_lang), placeholder="citizen@gmail.com")
                reg_pass = st.text_input(t("password", cur_lang), type="password")
                reg_phone = st.text_input(t("phone", cur_lang), placeholder="+91 9876543210")
                reg_age = st.number_input(t("age", cur_lang), min_value=14, max_value=85, value=21)
            with rc2:
                # Correction 1: Gender option 3 is Others
                reg_gender = st.selectbox(t("gender", cur_lang), GENDER_OPTIONS, index=0)
                reg_qual = st.selectbox(t("qualification", cur_lang), ["None", "8th", "10th", "12th", "Diploma", "Graduate", "Post Graduate"], index=3)
                reg_cat = st.selectbox(t("category", cur_lang), ["General", "OBC", "SC", "ST", "EWS"], index=0)
                # Correction 2: Complete Indian States & UTs
                reg_state = st.selectbox(t("state", cur_lang), ALL_INDIAN_STATES, index=0)
                reg_occ = st.selectbox(t("occupation", cur_lang), ["Student", "Unemployed", "Farmer", "Artisan", "Self-Employed", "Any"], index=0)

            btn_submit_reg = st.form_submit_button(t("register_btn", cur_lang))

        if btn_submit_reg:
            if not reg_name or not reg_email or not reg_pass:
                st.error("Please fill in Name, Email, and Password.")
            elif not is_valid_email(reg_email):
                # Correction 3: Email validation
                st.error("Please enter a valid email address (e.g. citizen@gmail.com).")
            else:
                res_reg = AuthService.register(
                    name=reg_name,
                    email=reg_email,
                    password=reg_pass,
                    phone=reg_phone,
                    age=reg_age,
                    gender=reg_gender,
                    qualification=reg_qual,
                    category=reg_cat,
                    state=reg_state,
                    occupation=reg_occ
                )
                if res_reg["success"]:
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = reg_email.strip().lower()
                    st.success("Account created successfully! Loading portal...")
                    st.rerun()
                else:
                    st.error(res_reg["message"])

    st.stop()

# =========================================================================
# LOGGED IN CITIZEN PORTAL (MAIN DASHBOARD)
# =========================================================================
active_user = AuthService.get_user(st.session_state["user_email"])
user_profile = active_user.get("profile", {})
user_settings = active_user.get("settings", {})

# 5 Main Service Tabs
tab_elig, tab_ocr, tab_schemes, tab_jobs, tab_profile_locker = st.tabs([
    f"🎯 {t('tab_services', cur_lang)}",
    f"📄 {t('tab_ocr', cur_lang)}",
    f"🏛️ {t('tab_search', cur_lang)}",
    f"📢 {t('tab_jobs', cur_lang)}",
    f"👤 {t('tab_profile', cur_lang)}"
])

# =========================================================================
# TAB 1: ELIGIBILITY EVALUATOR (SEPARATED SCHEMES / JOBS SELECTION)
# =========================================================================
with tab_elig:
    st.subheader(t("tab_services", cur_lang))
    st.caption("AI-powered evaluation of your personal criteria against active Central & State welfare schemes and recruitment notifications.")
    
    # Correction 6: Separate selection of eligibility between schemes and jobs
    st.markdown("##### **Select Category to Evaluate / मूल्यांकन श्रेणी चुनें:**")
    eval_category = st.radio(
        "Evaluation Category",
        options=[
            "🏛️ Welfare Schemes Eligibility",
            "💼 Government Jobs & Recruitment Eligibility",
            "🌟 Both Schemes & Jobs"
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    with st.form("match_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            q_age = st.number_input(t("age", cur_lang), min_value=14, max_value=85, value=user_profile.get("age", 21))
            # Correction 1: Others option for gender
            saved_gender = user_profile.get("gender", "Male")
            g_idx = GENDER_OPTIONS.index(saved_gender) if saved_gender in GENDER_OPTIONS else (2 if saved_gender == "All" else 0)
            q_gender = st.selectbox(t("gender", cur_lang), GENDER_OPTIONS, index=g_idx)
        with col2:
            qual_opts = ["None", "8th", "10th", "12th", "Diploma", "Graduate", "Post Graduate"]
            q_idx = qual_opts.index(user_profile.get("qualification", "12th")) if user_profile.get("qualification") in qual_opts else 3
            q_qual = st.selectbox(t("qualification", cur_lang), qual_opts, index=q_idx)
            q_income = st.number_input(t("annual_income", cur_lang), value=user_profile.get("annual_income", 150000), step=10000)
        with col3:
            cat_opts = ["General", "OBC", "SC", "ST", "EWS"]
            c_idx = cat_opts.index(user_profile.get("caste_category", "General")) if user_profile.get("caste_category") in cat_opts else 0
            q_cat = st.selectbox(t("category", cur_lang), cat_opts, index=c_idx)
            # Correction 2: All Indian States & UTs
            saved_state = user_profile.get("state", "All India")
            s_idx = ALL_INDIAN_STATES.index(saved_state) if saved_state in ALL_INDIAN_STATES else 0
            q_state = st.selectbox(t("state", cur_lang), ALL_INDIAN_STATES, index=s_idx)

        # Dynamic button label based on chosen category
        if "Schemes" in eval_category and "Both" not in eval_category:
            btn_label = "🔍 Evaluate Welfare Schemes Eligibility" if cur_lang == "en" else "🔍 कल्याणकारी योजना पात्रता जांचें"
        elif "Jobs" in eval_category and "Both" not in eval_category:
            btn_label = "🔍 Evaluate Government Jobs Eligibility" if cur_lang == "en" else "🔍 सरकारी भर्ती पात्रता जांचें"
        else:
            btn_label = "🔍 Evaluate Both Schemes & Jobs" if cur_lang == "en" else "🔍 योजनाएं एवं नौकरियां दोनों जांचें"

        btn_run_match = st.form_submit_button(btn_label)

    if btn_run_match:
        from app.core.schemas import UserProfileInput
        user_in = UserProfileInput(
            age=q_age,
            gender=q_gender,
            qualification=q_qual,
            annual_income=q_income,
            caste_category=q_cat,
            state=q_state,
            occupation="Student",
            preferred_language=cur_lang
        )
        with st.spinner("Evaluating citizen eligibility across neural network and official criteria..."):
            matcher = EligibilityMatcher.get_instance()
            results = matcher.match_all(user_in)

        show_schemes = "Schemes" in eval_category or "Both" in eval_category
        show_jobs = "Jobs" in eval_category or "Both" in eval_category

        # Evaluation Summary Card
        summary_title = ""
        if show_schemes and show_jobs:
            summary_title = f"Found <b>{results['eligible_schemes_count']}</b> Potentially Eligible Schemes & <b>{results['eligible_jobs_count']}</b> Matching Vacancies"
        elif show_schemes:
            summary_title = f"Found <b>{results['eligible_schemes_count']}</b> Potentially Eligible Welfare Schemes"
        else:
            summary_title = f"Found <b>{results['eligible_jobs_count']}</b> Matching Government Recruitments"

        eval_summary_html = (
            f'<div class="gov-card" style="border-left: 4px solid #1E3A8A;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">'
            f'<div>'
            f'<span class="badge-gov badge-navy">EVALUATION SUMMARY</span>'
            f'<h4 style="margin:4px 0 2px 0; color:#0F172A;">{summary_title}</h4>'
            f'<span style="color:#64748B; font-size:12.5px;">Preliminary match based on self-reported criteria. Please review official gazette requirements before applying.</span>'
            f'</div>'
            f'<span class="badge-gov badge-slate">AI MATCH CONFIDENCE: HIGH</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(eval_summary_html, unsafe_allow_html=True)

        # 1. Schemes Section (Rendered only if selected)
        if show_schemes:
            st.markdown(f"### 🏛️ {'Potentially Eligible Welfare Schemes' if cur_lang == 'en' else 'पात्र सरकारी योजनाएं'}")
            if results["eligible_schemes"]:
                for s in results["eligible_schemes"]:
                    with st.container():
                        # Correction 4: Check if key benefit is valid; do NOT show if None or empty
                        benefit_raw = s.get('benefits_en' if cur_lang == 'en' else 'benefits_hi')
                        benefit_html = ""
                        if benefit_raw and str(benefit_raw).strip().lower() not in ["none", "null", "n/a", "nil", ""]:
                            benefit_html = (
                                f'<div style="background:#F8FAFC; border-radius:6px; padding:8px 12px; margin-bottom:8px;">'
                                f'<span style="color:#065F46; font-size:13px; font-weight:600;">💰 Key Benefit: {benefit_raw}</span>'
                                f'</div>'
                            )

                        scheme_title = s['title_en'] if cur_lang == 'en' else s['title_hi']
                        scheme_cat = s.get('category', 'Welfare')
                        scheme_summary = s.get('summary_en' if cur_lang == 'en' else 'summary_hi', '')

                        scheme_card_html = (
                            f'<div class="card-scheme">'
                            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
                            f'<span class="badge-gov badge-green">POTENTIALLY ELIGIBLE</span>'
                            f'<span class="badge-gov badge-slate">{scheme_cat}</span>'
                            f'</div>'
                            f'<h4 style="margin:8px 0 4px 0; color:#0F172A;">{scheme_title}</h4>'
                            f'<p style="color:#334155; font-size:14px; margin:4px 0 8px 0;">{scheme_summary}</p>'
                            f'{benefit_html}'
                            f'</div>'
                        )
                        st.markdown(scheme_card_html, unsafe_allow_html=True)
                        st.link_button(f"🔗 {t('apply_portal', cur_lang)}", s["application_url"])
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            else:
                st.info("No welfare schemes matched your specific combination of age, income, and category. Try adjusting criteria.")

        # 2. Jobs Section (Rendered only if selected)
        if show_jobs:
            st.markdown(f"### 💼 {'Matching Government Recruitment Vacancies' if cur_lang == 'en' else 'योग्यता अनुसार सरकारी रिक्तियां'}")
            if results["eligible_jobs"]:
                for j in results["eligible_jobs"]:
                    with st.container():
                        job_title = j['title_en'] if cur_lang == 'en' else j['title_hi']
                        job_deadline = j.get('application_deadline', 'Open')
                        job_org = j.get('organization', 'Government Agency')
                        job_qual = j.get('qualification_required', '10th/12th/Graduate')
                        job_vac = j.get('vacancies', 'Not Specified')
                        job_sum = j.get('summary_en' if cur_lang == 'en' else 'summary_hi', '')
                        portal_link = j.get('official_portal', 'https://india.gov.in')

                        # Clean unindented HTML to eliminate code block parsing
                        job_card_html = (
                            f'<div class="card-job">'
                            f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
                            f'<span class="badge-gov badge-navy">CENTRAL / STATE RECRUITMENT</span>'
                            f'<span class="badge-gov badge-red">⏰ DEADLINE: {job_deadline}</span>'
                            f'</div>'
                            f'<h4 style="margin:8px 0 2px 0; color:#0F172A;">{job_title}</h4>'
                            f'<span style="color:#1E3A8A; font-weight:600; font-size:13px;">Organization: {job_org}</span>'
                            f'<div style="display:flex; gap:12px; margin:8px 0; flex-wrap:wrap;">'
                            f'<span style="font-size:12.5px; color:#475569;"><b>Qualification:</b> {job_qual}</span>'
                            f'<span style="font-size:12.5px; color:#475569;"><b>Vacancies:</b> {job_vac}</span>'
                            f'</div>'
                            f'<p style="color:#334155; font-size:14px; margin:4px 0 8px 0;">{job_sum}</p>'
                            f'</div>'
                        )
                        st.markdown(job_card_html, unsafe_allow_html=True)
                        st.link_button(f"🔗 {t('apply_portal', cur_lang)}", portal_link)
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            else:
                st.info("No active government recruitments match your qualification criteria at this moment.")

# =========================================================================
# TAB 2: DOCUMENT OCR & EXPLAINER (NEWSPAPERS, TENDERS, APPLICATION SITES)
# =========================================================================
with tab_ocr:
    st.subheader(t("ocr_header", cur_lang))
    st.caption("Upload scanned government circulars, newspaper notices, e-tenders (NIT), or recruitment flyers in PDF or image formats.")
    
    # Visual Process Pipeline Indicator
    st.markdown(
        '<div class="process-bar">'
        '<div class="process-step-item"><span>📤</span> 1. Upload Notice</div>'
        '<span class="process-arrow">➔</span>'
        '<div class="process-step-item"><span>📖</span> 2. Document OCR Scan</div>'
        '<span class="process-arrow">➔</span>'
        '<div class="process-step-item"><span>🔤</span> 3. Extract Text</div>'
        '<span class="process-arrow">➔</span>'
        '<div class="process-step-item"><span>💡</span> 4. AI Simplification</div>'
        '<span class="process-arrow">➔</span>'
        '<div class="process-step-item"><span>✅</span> 5. Verify & Apply</div>'
        '</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        t("ocr_prompt", cur_lang),
        type=["pdf", "png", "jpg", "jpeg", "bmp", "webp", "tiff"],
        help="Supports official gazette notices, e-tenders, employment advertisements, and welfare notifications."
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        
        col_prev, col_go = st.columns([1, 2])
        with col_prev:
            if uploaded_file.type.startswith("image"):
                st.image(file_bytes, caption="Uploaded Notice Preview", use_container_width=True)
            else:
                pdf_preview_html = (
                    f'<div class="gov-card" style="text-align:center;">'
                    f'<span style="font-size:32px;">📄</span><br>'
                    f'<b>{uploaded_file.name}</b><br>'
                    f'<span style="color:#64748B; font-size:12px;">PDF Document ({len(file_bytes)//1024} KB)</span>'
                    f'</div>'
                )
                st.markdown(pdf_preview_html, unsafe_allow_html=True)

        with col_go:
            if st.button(f"🔍 {t('analyze_btn', cur_lang)}", type="primary"):
                with st.spinner("Extracting text via EasyOCR & analyzing administrative structure..."):
                    ocr = DocumentOCRService.get_instance()
                    ocr_res = ocr.process_file(file_bytes, uploaded_file.name)

                    analyzer = DocumentAnalyzer.get_instance()
                    doc_analysis = analyzer.analyze_document(
                        ocr_res["extracted_text"],
                        preferred_language=cur_lang
                    )

                category = doc_analysis.get("document_category", "general")
                doc_type_title = doc_analysis.get("document_type", "Official Notice")
                authority = doc_analysis.get("issuing_authority", "Competent Authority")
                ref_no = doc_analysis.get("reference_number", "N/A")
                deadline = doc_analysis.get("deadline", "Refer to notice")
                portal_url = doc_analysis.get("official_url", "https://india.gov.in")
                portal_name = doc_analysis.get("official_portal_name", "Official Government Portal")

                # Trust & Verification Classification Card
                doc_header_html = (
                    f'<div class="gov-card" style="border-top: 3px solid #1E3A8A;">'
                    f'<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">'
                    f'<div>'
                    f'<div style="display:flex; gap:6px; margin-bottom:6px; flex-wrap:wrap;">'
                    f'<span class="badge-gov badge-navy">{category.upper()} CLASSIFIED</span>'
                    f'<span class="badge-gov badge-slate">USER UPLOADED DOCUMENT</span>'
                    f'</div>'
                    f'<h3 style="color: #0F172A !important; margin: 4px 0 2px 0; font-size: 19px; font-weight: 800;">'
                    f'📜 {doc_type_title}'
                    f'</h3>'
                    f'<span style="color: #475569; font-size: 13px; font-weight: 600;">{t("authority", cur_lang)}: {authority}</span>'
                    f'</div>'
                    f'<div style="text-align: right;">'
                    f'<span style="color: #64748B; font-size: 12px; font-weight:600;">Reference / NIT No:</span><br>'
                    f'<code style="background: #F1F5F9; color: #0F172A; padding: 4px 10px; border-radius: 6px; border: 1px solid #CBD5E1; font-weight: 700; font-size:12.5px;">{ref_no}</code>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(doc_header_html, unsafe_allow_html=True)

                # Trust Verification Notice Banner
                st.markdown(
                    '<div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; display:flex; align-items:center; gap:10px;">'
                    '<span style="font-size:18px;">🛡️</span>'
                    '<span style="font-size: 12.5px; color: #475569; line-height: 1.4;">'
                    '<b>AI Simplified Explanation:</b> The interpretation below is generated for citizen clarity. For legal validity, always verify with the official gazette publication.'
                    '</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # What Exactly Does This Document Mean?
                meaning_text = doc_analysis.get('what_it_means_first', '')
                meaning_html = (
                    f'<div class="gov-card">'
                    f'<div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">'
                    f'<h4 style="color: #1E3A8A !important; margin: 0; font-weight: 700; font-size: 16px;">💡 {t("what_it_means", cur_lang)}</h4>'
                    f'<span class="badge-gov badge-slate">SIMPLE CITIZEN SUMMARY</span>'
                    f'</div>'
                    f'<div style="font-size: 14.5px; color: #1E293B !important; line-height: 1.65; white-space: pre-line;">{meaning_text}</div>'
                    f'</div>'
                )
                st.markdown(meaning_html, unsafe_allow_html=True)

                # 4-Card Structured Grid
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    dead_html = (
                        f'<div class="card-deadline">'
                        f'<span class="badge-gov badge-red">⏰ {t("deadlines", cur_lang).upper()}</span><br>'
                        f'<b style="font-size: 14.5px; color: #991B1B; display:inline-block; margin-top:6px;">{deadline}</b>'
                        f'</div>'
                    )
                    st.markdown(dead_html, unsafe_allow_html=True)

                    elig_for_html = (
                        f'<div class="card-tender">'
                        f'<span class="badge-gov badge-amber">👥 {t("eligibility", cur_lang).upper()}</span><br>'
                        f'<span style="font-size: 13.5px; color: #92400E; display:inline-block; margin-top:6px;">{doc_analysis.get("who_is_it_for")}</span>'
                        f'</div>'
                    )
                    st.markdown(elig_for_html, unsafe_allow_html=True)

                with c_f2:
                    fin_html = (
                        f'<div class="card-scheme">'
                        f'<span class="badge-gov badge-green">💰 {t("financials", cur_lang).upper()}</span><br>'
                        f'<span style="font-size: 13.5px; color: #065F46; display:inline-block; margin-top:6px;">{doc_analysis.get("key_benefits")}</span>'
                        f'</div>'
                    )
                    st.markdown(fin_html, unsafe_allow_html=True)

                    auth_html = (
                        f'<div class="card-teal">'
                        f'<span class="badge-gov badge-teal">🏛️ {t("authority", cur_lang).upper()}</span><br>'
                        f'<span style="font-size: 13.5px; color: #0F766E; display:inline-block; margin-top:6px;">{authority} (Ref: {ref_no})</span>'
                        f'</div>'
                    )
                    st.markdown(auth_html, unsafe_allow_html=True)

                # Step-by-Step Action Guide
                st.markdown(f"### 📋 {t('action_steps', cur_lang)}")
                for idx, step in enumerate(doc_analysis.get("action_steps", []), 1):
                    step_html = (
                        f'<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display:flex; align-items:center; gap:10px;">'
                        f'<span style="background:#EFF6FF; color:#1E40AF; width:24px; height:24px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:700; font-size:12px;">{idx}</span>'
                        f'<span style="color: #1E293B; font-weight: 500; font-size: 14px;">{step}</span>'
                        f'</div>'
                    )
                    st.markdown(step_html, unsafe_allow_html=True)

                # Direct Official Portal Action
                st.markdown(f"### 🔗 {t('related_portals', cur_lang)}")
                col_btn, col_info = st.columns([1, 2])
                with col_btn:
                    st.link_button(f"🌐 {t('apply_portal', cur_lang)}", portal_url)
                with col_info:
                    portal_info_html = (
                        f'<div style="padding-top:6px;">'
                        f'<span class="badge-gov badge-green">VERIFIED OFFICIAL PORTAL</span><br>'
                        f'<span style="color:#475569; font-size:13px;">Authority: <b>{portal_name}</b> | URL: <code>{portal_url}</code></span>'
                        f'</div>'
                    )
                    st.markdown(portal_info_html, unsafe_allow_html=True)

                # Safety & Anti-Scam Advisory Notice
                safety_html = (
                    f'<div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #D97706; border-radius: 8px; padding: 12px 16px; margin-top: 14px;">'
                    f'<span style="color: #92400E; font-weight: 700; font-size: 13px;">🛡️ {t("safety_tip", cur_lang)}:</span><br>'
                    f'<span style="color: #78350F; font-size: 13px; line-height: 1.5;">{doc_analysis.get("safety_guidance")}</span>'
                    f'</div>'
                )
                st.markdown(safety_html, unsafe_allow_html=True)

                # Raw Scanned Text (Original Document OCR)
                with st.expander("🔍 View Raw Extracted Text from Document (OCR Output)"):
                    st.caption(f"Characters extracted: {ocr_res.get('character_count', 0)} | Method: {ocr_res.get('extraction_method', 'EasyOCR')}")
                    st.code(ocr_res.get("extracted_text", ""), language="text")

# =========================================================================
# TAB 3: SCHEMES DIRECTORY & SEARCH
# =========================================================================
with tab_schemes:
    st.subheader(t("scheme_search_header", cur_lang))
    st.caption("Search across Central and State government welfare schemes using semantic cross-lingual search in English, Hindi, or regional languages.")
    
    # Elevated Prominent Search Experience
    st.markdown(
        '<div class="search-card-wrapper">'
        '<label style="font-weight:700; font-size:14px; color:#1E3A8A; display:block; margin-bottom:4px;">'
        '🔎 Search Government Welfare Schemes & Subsidies'
        '</label>'
        '<span style="font-size:12.5px; color:#64748B;">Enter keywords in Hindi, English or regional languages (e.g., किसान सम्मान, scholarship, आवास योजना)</span>'
        '</div>',
        unsafe_allow_html=True
    )

    query_scheme = st.text_input(
        "Search Welfare Schemes",
        value="Financial assistance for small farmers" if cur_lang == "en" else "गरीब किसानों के लिए सरकारी सहायता",
        label_visibility="collapsed",
        placeholder="Search government schemes, scholarships, subsidies (e.g. PM Kisan, Post-Matric, Ayushman)..."
    )
    
    col_s1, col_s2 = st.columns([1, 4])
    with col_s1:
        run_search = st.button(f"🔍 {t('search_btn', cur_lang)}", type="primary")

    if run_search or query_scheme:
        with st.spinner("Searching multilingual government schemes vector database..."):
            rag = MultilingualRAGEngine.get_instance()
            schemes_found = rag.search_schemes(query_scheme, top_k=5)

        st.markdown(f"### 🏛️ Matched Schemes ({len(schemes_found)})")
        if schemes_found:
            for sc in schemes_found:
                with st.container():
                    sc_title = sc['title_en'] if cur_lang == 'en' else sc['title_hi']
                    sc_cat = sc.get('category', 'Welfare Scheme')
                    sc_score = int(sc['similarity_score'] * 100)
                    sc_sum = sc.get('summary_en' if cur_lang == 'en' else 'summary_hi', '')
                    
                    # Correction 4: Check if benefit is valid; do not show if None
                    sc_b = sc.get('benefits_en' if cur_lang == 'en' else 'benefits_hi')
                    sc_benefit_html = ""
                    if sc_b and str(sc_b).strip().lower() not in ["none", "null", "n/a", "nil", ""]:
                        sc_benefit_html = (
                            f'<div style="background:#F8FAFC; border-radius:6px; padding:8px 12px; margin-bottom:8px;">'
                            f'<span style="color:#065F46; font-size:13px; font-weight:600;">💰 Benefits: {sc_b}</span>'
                            f'</div>'
                        )

                    scheme_item_html = (
                        f'<div class="gov-card">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
                        f'<span class="badge-gov badge-navy">{sc_cat}</span>'
                        f'<span class="badge-gov badge-green">RELEVANCE: {sc_score}%</span>'
                        f'</div>'
                        f'<h4 style="margin:8px 0 4px 0; color:#0F172A;">{sc_title}</h4>'
                        f'<p style="color:#334155; font-size:14px; margin:4px 0 8px 0;">{sc_sum}</p>'
                        f'{sc_benefit_html}'
                        f'</div>'
                    )
                    st.markdown(scheme_item_html, unsafe_allow_html=True)
                    st.link_button(f"🔗 {t('apply_portal', cur_lang)}", sc["application_url"])
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        else:
            st.info("No matching schemes found for your search query. Try broader keywords like 'education', 'farmer', 'health', or 'housing'.")

# =========================================================================
# TAB 4: RECENT GOVERNMENT RECRUITMENT NOTIFICATIONS
# =========================================================================
with tab_jobs:
    st.subheader(t("tab_jobs", cur_lang))
    st.caption("Active central and state government recruitment notifications categorized by minimum educational qualification.")
    
    col_jq, col_jc = st.columns([2, 3])
    with col_jq:
        qual_choice = st.selectbox(
            "Filter by Minimum Qualification",
            ["All", "10th", "12th", "Graduate"]
        )
    
    all_jobs_list = DatasetLoader.load_jobs()
    if qual_choice != "All":
        disp_jobs = [j for j in all_jobs_list if j.get("qualification_required") == qual_choice]
    else:
        disp_jobs = all_jobs_list
        
    with col_jc:
        badge_header_html = (
            f'<div style="padding-top:28px;">'
            f'<span class="badge-gov badge-navy">ACTIVE RECRUITMENTS: {len(disp_jobs)}</span> '
            f'<span class="badge-gov badge-green">100% OFFICIAL ADVERTISEMENTS</span>'
            f'</div>'
        )
        st.markdown(badge_header_html, unsafe_allow_html=True)
    
    st.divider()

    # Correction 5: Clean unindented card without any empty lines inside HTML to completely prevent code block rendering
    for job in disp_jobs:
        with st.container():
            job_title = job.get('title_en' if cur_lang == 'en' else 'title_hi', '')
            job_org = job.get('organization', 'Government Agency')
            job_deadline = job.get('application_deadline', 'Open')
            job_qual = job.get('qualification_required', '10th/12th/Graduate')
            job_vac = job.get('vacancies', 'Not Specified')
            job_loc = job.get('location', 'All India')
            job_sum = job.get('summary_en' if cur_lang == 'en' else 'summary_hi', '')
            portal_url = job.get('official_portal', 'https://india.gov.in')

            job_card_clean_html = (
                f'<div class="gov-card">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
                f'<span class="badge-gov badge-navy">CENTRAL RECRUITMENT</span>'
                f'<span class="badge-gov badge-red">⏰ DEADLINE: {job_deadline}</span>'
                f'</div>'
                f'<h4 style="margin:8px 0 2px 0; color:#0F172A; font-size:17px;">🎖️ {job_title}</h4>'
                f'<span style="color:#1E3A8A; font-weight:700; font-size:13.5px;">Organization: {job_org}</span>'
                f'<div style="display:flex; gap:10px; margin:10px 0; flex-wrap:wrap;">'
                f'<span class="badge-gov badge-slate">🎓 MIN QUAL: {job_qual}</span>'
                f'<span class="badge-gov badge-amber">👥 VACANCIES: {job_vac}</span>'
                f'<span class="badge-gov badge-teal">📍 LOCATION: {job_loc}</span>'
                f'<span class="badge-gov badge-green">🟢 APPLICATION OPEN</span>'
                f'</div>'
                f'<p style="color:#334155; font-size:14px; margin:6px 0 10px 0; line-height:1.5;">{job_sum}</p>'
                f'</div>'
            )
            st.markdown(job_card_clean_html, unsafe_allow_html=True)
            st.link_button(f"🔗 {t('apply_portal', cur_lang)}", portal_url)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# =========================================================================
# TAB 5: PROFILE, APPLICATIONS, EXAMS & CITIZEN LOCKER
# =========================================================================
with tab_profile_locker:
    st.subheader(t("tab_profile", cur_lang))
    st.caption("Manage your citizen demographic profile, store submitted application numbers, track exam attempts, and set alert preferences.")
    
    qual_opts = ["None", "8th", "10th", "12th", "Diploma", "Graduate", "Post Graduate"]
    cat_opts = ["General", "OBC", "SC", "ST", "EWS"]

    # Section 1: Profile Details Editor
    with st.expander("👤 1. Personal Citizen Profile Details", expanded=True):
        with st.form("profile_update_form"):
            p1, p2, p3 = st.columns(3)
            with p1:
                u_name = st.text_input(t("full_name", cur_lang), value=user_profile.get("full_name", ""))
                u_age = st.number_input(t("age", cur_lang), min_value=14, max_value=85, value=user_profile.get("age", 21))
                # Correction 1: Others option for gender
                u_saved_gen = user_profile.get("gender", "Male")
                u_g_idx = GENDER_OPTIONS.index(u_saved_gen) if u_saved_gen in GENDER_OPTIONS else (2 if u_saved_gen == "All" else 0)
                u_gender = st.selectbox(t("gender", cur_lang), GENDER_OPTIONS, index=u_g_idx)
            with p2:
                q_idx = qual_opts.index(user_profile.get("qualification", "12th")) if user_profile.get("qualification") in qual_opts else 3
                u_qual = st.selectbox(t("qualification", cur_lang), qual_opts, index=q_idx)
                u_income = st.number_input(t("annual_income", cur_lang), value=user_profile.get("annual_income", 150000), step=10000)
                c_idx = cat_opts.index(user_profile.get("caste_category", "General")) if user_profile.get("caste_category") in cat_opts else 0
                u_cat = st.selectbox(t("category", cur_lang), cat_opts, index=c_idx)
            with p3:
                # Correction 2: All Indian States & UTs
                u_saved_st = user_profile.get("state", "All India")
                u_s_idx = ALL_INDIAN_STATES.index(u_saved_st) if u_saved_st in ALL_INDIAN_STATES else 0
                u_state = st.selectbox(t("state", cur_lang), ALL_INDIAN_STATES, index=u_s_idx)
                u_occ = st.selectbox(t("occupation", cur_lang), ["Student", "Unemployed", "Farmer", "Artisan", "Self-Employed", "Any"], index=0)
                u_phone = st.text_input(t("phone", cur_lang), value=user_profile.get("phone", ""))

            save_p_btn = st.form_submit_button(f"💾 {t('save_profile_btn', cur_lang)}")
            if save_p_btn:
                updated_profile = {
                    "full_name": u_name.strip(),
                    "age": u_age,
                    "gender": u_gender,
                    "qualification": u_qual,
                    "annual_income": u_income,
                    "caste_category": u_cat,
                    "state": u_state,
                    "occupation": u_occ,
                    "phone": u_phone.strip(),
                    "email": st.session_state["user_email"]
                }
                AuthService.update_profile(st.session_state["user_email"], updated_profile)
                st.success("Citizen profile updated successfully!")
                st.rerun()

    # Section 2: Submitted Applications Tracker
    with st.expander("📋 2. Submitted Applications & Forms Tracker", expanded=False):
        user_apps = active_user.get("applications_filled", [])
        if user_apps:
            for idx, a_item in enumerate(user_apps):
                with st.container():
                    ca1, ca2, ca3 = st.columns([3, 2, 1])
                    with ca1:
                        st.markdown(f"**{a_item.get('title')}**")
                        st.caption(f"Application No: `{a_item.get('app_id')}` | Date: {a_item.get('applied_date')}")
                    with ca2:
                        status_html = f'<span class="badge-gov badge-green">STATUS: {a_item.get("status")}</span>'
                        st.markdown(status_html, unsafe_allow_html=True)
                    with ca3:
                        st.link_button("Portal", a_item.get("official_portal", "https://india.gov.in"))
                        if st.button("Delete", key=f"del_uapp_{idx}"):
                            AuthService.delete_application(st.session_state["user_email"], idx)
                            st.rerun()
                    st.divider()
        else:
            st.info("No applications recorded yet. Add your submitted applications to track status and key dates.")

        # Add Application Form
        with st.form("add_user_app_form"):
            st.markdown("##### ➕ Add Submitted Application")
            c_ua1, c_ua2 = st.columns(2)
            with c_ua1:
                app_t = st.text_input("Scheme / Exam Name", placeholder="e.g. Post-Matric Scholarship")
                app_i = st.text_input("Application Number", placeholder="APP-2026-9812")
            with c_ua2:
                app_s = st.selectbox("Current Status", ["Under Verification", "Approved - DBT Credited", "Admit Card Released", "Submitted"])
                app_p = st.text_input("Portal Link", "https://myscheme.gov.in")
            
            sub_uapp = st.form_submit_button(t("add_app_btn", cur_lang))
            if sub_uapp and app_t:
                AuthService.add_application(st.session_state["user_email"], {
                    "app_id": app_i or "APP-2026",
                    "title": app_t,
                    "applied_date": datetime.today().strftime('%Y-%m-%d'),
                    "status": app_s,
                    "official_portal": app_p
                })
                st.success("Application recorded successfully!")
                st.rerun()

    # Section 3: Past Examinations & Declared Results
    with st.expander("🎓 3. Past Examinations & Declared Results Tracker", expanded=False):
        user_exams = active_user.get("past_exams", [])
        if user_exams:
            for e_idx, e_item in enumerate(user_exams):
                with st.container():
                    ce1, ce2, ce3 = st.columns([3, 2, 1])
                    with ce1:
                        st.markdown(f"**{e_item.get('exam_name')}** ({e_item.get('organization')})")
                        st.caption(f"Roll No: `{e_item.get('roll_number')}` | Exam Date: {e_item.get('exam_date')}")
                    with ce2:
                        exam_status_html = (
                            f'<span class="badge-gov badge-navy">{e_item.get("status")}</span>'
                            f'<div style="color:#64748B; font-size:12px; margin-top:4px;">Score: {e_item.get("score")} | Declared: {e_item.get("result_date")}</div>'
                        )
                        st.markdown(exam_status_html, unsafe_allow_html=True)
                    with ce3:
                        if st.button("Delete", key=f"del_uex_{e_idx}"):
                            AuthService.delete_exam(st.session_state["user_email"], e_idx)
                            st.rerun()
                    st.divider()
        else:
            st.info("No past examination records added yet. Store your roll numbers and results here.")

        # Add Exam Form
        with st.form("add_user_exam_form"):
            st.markdown("##### ➕ Add Exam Attempt & Result")
            c_ue1, c_ue2 = st.columns(2)
            with c_ue1:
                ex_n = st.text_input("Examination Name", placeholder="e.g. SSC GD Constable")
                ex_o = st.text_input("Conducting Organization", "SSC")
                ex_r = st.text_input("Roll Number", "2401089201")
            with c_ue2:
                ex_sc = st.text_input("Marks / Score", placeholder="e.g. 136 / 160")
                ex_st = st.selectbox("Result Status", ["Declared - Qualified", "Declared - Not Qualified", "Waiting for Result"])
                ex_dt = st.date_input("Result Date")

            sub_uex = st.form_submit_button(t("add_exam_btn", cur_lang))
            if sub_uex and ex_n:
                AuthService.add_exam(st.session_state["user_email"], {
                    "exam_name": ex_n,
                    "organization": ex_o,
                    "roll_number": ex_r,
                    "exam_date": datetime.today().strftime('%Y-%m-%d'),
                    "result_date": str(ex_dt),
                    "status": ex_st,
                    "score": ex_sc or "N/A"
                })
                st.success("Exam record added successfully!")
                st.rerun()

    # Section 4: Daily Notification & Account Settings
    with st.expander("⚙️ 4. Daily Notification & Portal Settings", expanded=False):
        with st.form("settings_form"):
            st.markdown("##### Manage your daily alerts and notifications")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                set_jobs = st.checkbox(t("daily_job_alerts", cur_lang), value=user_settings.get("daily_job_alerts", True))
                set_schemes = st.checkbox(t("daily_scheme_alerts", cur_lang), value=user_settings.get("daily_scheme_alerts", True))
            with s_col2:
                freq_opts = ["Daily", "Weekly", "Instant"]
                f_idx = freq_opts.index(user_settings.get("notification_frequency", "Daily")) if user_settings.get("notification_frequency") in freq_opts else 0
                set_freq = st.selectbox(t("alert_frequency", cur_lang), freq_opts, index=f_idx)
            
            btn_save_settings = st.form_submit_button(f"💾 {t('save_settings_btn', cur_lang)}")
            if btn_save_settings:
                new_settings = {
                    "daily_job_alerts": set_jobs,
                    "daily_scheme_alerts": set_schemes,
                    "notification_frequency": set_freq,
                    "preferred_language": cur_lang
                }
                AuthService.update_settings(st.session_state["user_email"], new_settings)
                st.success("Settings saved successfully!")
                st.rerun()

# Dignified National Public Service Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B !important; font-size: 13px; font-weight: 500; line-height: 1.6;'>"
    "🏛️ <b>National Digital Scheme & Employment Assistance Portal</b> • A Digital India Public Good Initiative<br>"
    "Ministry of Electronics & Information Technology • Governed under National e-Governance Plan (NeGP) • 100% Free Public Service"
    "</div>",
    unsafe_allow_html=True
)
