import os
import html
from datetime import date, datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(page_title="School EMIS", page_icon="🏫", layout="wide")

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        --ink: #f4f0e8;
        --muted: #a9a39a;
        --panel: rgba(21, 21, 21, 0.88);
        --panel-soft: rgba(255, 255, 255, 0.045);
        --line: rgba(244, 240, 232, 0.12);
        --gold: #d6b36a;
        --gold-soft: rgba(214, 179, 106, 0.16);
    }
    html, body, [class*="css"] {
        font-family: "Aptos", "Segoe UI", sans-serif;
        letter-spacing: 0.01em;
    }
    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(214, 179, 106, 0.10), transparent 30%),
            linear-gradient(135deg, #050505 0%, #0b0b0b 48%, #11100e 100%);
        color: var(--ink);
    }
    .block-container {
        max-width: 1440px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 {
        color: var(--ink) !important;
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: 0;
    }
    h1 {
        font-size: clamp(2rem, 4vw, 3.5rem) !important;
        line-height: 1.05 !important;
        margin-bottom: 0.75rem !important;
    }
    h2 {
        font-size: 1.7rem !important;
        margin-top: 2rem !important;
    }
    h3 {
        font-size: 1.25rem !important;
    }
    p, label, .stCaption {
        color: var(--muted) !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d 0%, #151310 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p {
        color: var(--ink) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(5, 5, 5, 0.72);
        backdrop-filter: blur(14px);
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(35, 33, 29, 0.95), rgba(15, 15, 15, 0.95));
        border: 1px solid var(--line);
        border-top: 2px solid var(--gold);
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.22);
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink) !important;
        font-family: Georgia, "Times New Roman", serif;
    }
    div[data-testid="stForm"], .stExpander {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 12px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
        padding: 0.4rem;
    }
    input, textarea, [data-baseweb="select"] > div {
        background: #171614 !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
        border-radius: 8px !important;
    }
    input:focus, textarea:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 1px var(--gold-soft) !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
    }
    [data-baseweb="tab-list"] {
        gap: 0.4rem;
        border-bottom: 1px solid var(--line);
    }
    [data-baseweb="tab"] {
        color: var(--muted);
        padding: 0.75rem 1rem;
    }
    [aria-selected="true"] {
        color: var(--gold) !important;
        border-bottom-color: var(--gold) !important;
    }
    .stButton > button, .stDownloadButton > button {
        background: var(--gold);
        color: #17130b;
        border: 1px solid var(--gold);
        border-radius: 8px;
        min-height: 42px;
        font-weight: 700;
        opacity: 1;
        box-shadow: 0 8px 22px rgba(214, 179, 106, 0.16);
        transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #ebcc8b;
        color: #17130b;
        transform: translateY(-1px);
        box-shadow: 0 12px 28px rgba(214, 179, 106, 0.24);
    }
    [data-testid="stAlert"] {
        background: var(--panel-soft);
        border: 1px solid var(--line);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SIGNUP_TABLE = "student_signup"
ROLE_TABLES = {
    "admin": "admin_signup",
    "teacher": "teacher_signup",
    "principal": "principal_signup",
    "accountant": "accountant_signup",
    "librarian": "librarian_signup",
}


@st.cache_resource
def get_supabase_client():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return None
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as exc:
        st.error(f"Could not connect to Supabase: {exc}")
        return None


def seed_default_admin(supabase):
    try:
        st.session_state.admin_table_error = None
        admin_table = ROLE_TABLES["admin"]
        try:
            existing = supabase.table(admin_table).select("username").ilike("username", "admin").execute()
        except Exception as admin_table_error:
            if "PGRST205" not in str(admin_table_error) and "admin_signup" not in str(admin_table_error):
                raise
            admin_table = SIGNUP_TABLE
            existing = supabase.table(admin_table).select("username").ilike("username", "admin").execute()
        if not existing.data:
            admin_payload = {
                "full_name": "System Administrator",
                "phone": "",
                "email": "",
                "username": "admin",
                "password": "admin",
                "role": "admin",
            }
            if admin_table == SIGNUP_TABLE:
                admin_payload.update({
                    "admission_no": "",
                    "class_name": "",
                    "guardian_name": "",
                })
            supabase.table(admin_table).insert(admin_payload).execute()
    except Exception as exc:
        st.session_state.admin_table_error = str(exc)


def ensure_state():
    supabase = get_supabase_client()
    if supabase is None:
        st.error("Supabase is required. Set SUPABASE_URL and SUPABASE_KEY in .env.")
        st.stop()
    seed_default_admin(supabase)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_role" not in st.session_state:
        st.session_state.current_role = None
    if "current_student_id" not in st.session_state:
        st.session_state.current_student_id = None
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"


def load_students(supabase):
    return _load_table(supabase, "students", "created_at")


def load_attendance(supabase):
    return _load_table(supabase, "attendance", "attendance_date")


def load_fee_records(supabase):
    return _load_table(supabase, "fee_records", "payment_date")


def load_teachers(supabase):
    return _load_table(supabase, "teachers", "created_at")


def load_courses(supabase):
    return _load_table(supabase, "courses", "created_at")


def load_marks(supabase):
    return _load_table(supabase, "marks", "created_at")


def _load_table(supabase, table_name, order_column="created_at"):
    try:
        response = supabase.table(table_name).select("*").order(order_column, desc=True).execute()
        return response.data or []
    except Exception as exc:
        st.error(f"Could not load {table_name} from Supabase: {exc}")
        return []


def load_library_books(supabase):
    return _load_table(supabase, "library_books")


def load_library_loans(supabase):
    return _load_table(supabase, "library_loans")


def save_record(supabase, table_name, payload):
    try:
        supabase.table(table_name).insert(payload).execute()
        return True
    except Exception as exc:
        st.error(f"Could not save {table_name}: {exc}")
        return False


def update_record(supabase, table_name, record_id, payload):
    try:
        supabase.table(table_name).update(payload).eq("id", record_id).execute()
        return True
    except Exception as exc:
        st.error(f"Could not update {table_name}: {exc}")
        return False


def get_user_by_username(supabase, username, role=None):
    try:
        if role == "admin":
            tables = [ROLE_TABLES["admin"], SIGNUP_TABLE]
        elif role in ROLE_TABLES:
            tables = [ROLE_TABLES[role]]
        else:
            tables = [SIGNUP_TABLE, *ROLE_TABLES.values()]
        for table_name in tables:
            try:
                response = supabase.table(table_name).select("*").ilike("username", username).execute()
            except Exception:
                continue
            if not response.data:
                continue
            row = response.data[0]
            student_id = row.get("student_id")
            if student_id is None and row.get("admission_no"):
                student_response = supabase.table("students").select("id").eq("admission_no", row["admission_no"]).limit(1).execute()
                if student_response.data:
                    student_id = student_response.data[0].get("id")
            return {
                    "username": row.get("username"),
                    "password": row.get("password"),
                    "role": row.get("role"),
                    "full_name": row.get("full_name"),
                    "admission_no": row.get("admission_no"),
                    "class_name": row.get("class_name"),
                    "guardian_name": row.get("guardian_name"),
                    "phone": row.get("phone"),
                    "email": row.get("email"),
                    "student_id": student_id,
            }
    except Exception as exc:
        st.error(f"Could not look up user in Supabase: {exc}")
    return None


def create_user(supabase, username, password, role, student_id=None, staff_data=None):
    if not username or not password:
        st.error("Username and password are required")
        return False
    if get_user_by_username(supabase, username, role=role):
        st.error("That username already exists")
        return False

    staff_data = staff_data or {}
    try:
        payload = {
            "full_name": staff_data.get("full_name", ""),
            "phone": staff_data.get("phone", ""),
            "email": staff_data.get("email", ""),
            "username": username,
            "password": password,
            "role": role,
            "created_at": datetime.now().isoformat(),
        }
        if role == "teacher":
            payload["subject"] = staff_data.get("subject", "")
        supabase.table(ROLE_TABLES[role]).insert(payload).execute()
        return True
    except Exception as exc:
        st.error(f"Could not create the Supabase user: {exc}")
        return False


def add_student(supabase, student_data):
    try:
        supabase.table("students").insert(student_data).execute()
        return True
    except Exception as exc:
        st.error(f"Could not add student to Supabase: {exc}")
        return False


def update_student(supabase, student_id, student_data):
    try:
        supabase.table("students").update(student_data).eq("id", student_id).execute()
        return True
    except Exception as exc:
        st.error(f"Could not update student in Supabase: {exc}")
        return False


def delete_student(supabase, student_id):
    try:
        supabase.table("students").delete().eq("id", student_id).execute()
        return True
    except Exception as exc:
        st.error(f"Could not delete student from Supabase: {exc}")
        return False


def add_attendance(supabase, student_id, attendance_date, status):
    try:
        supabase.table("attendance").insert({"student_id": student_id, "attendance_date": str(attendance_date), "status": status}).execute()
        return True
    except Exception as exc:
        st.error(f"Could not record attendance in Supabase: {exc}")
        return False


def add_fee_record(supabase, student_id, amount, payment_date, status, note):
    try:
        supabase.table("fee_records").insert({"student_id": student_id, "amount": amount, "payment_date": str(payment_date), "status": status, "note": note}).execute()
        return True
    except Exception as exc:
        st.error(f"Could not save fee record to Supabase: {exc}")
        return False


def add_teacher(supabase, full_name, subject, phone, email):
    try:
        supabase.table("teachers").insert({"full_name": full_name, "subject": subject, "phone": phone, "email": email}).execute()
        return True
    except Exception as exc:
        st.error(f"Could not add teacher to Supabase: {exc}")
        return False


def add_course(supabase, course_name, class_name, teacher_name):
    try:
        supabase.table("courses").insert({"course_name": course_name, "class_name": class_name, "teacher_name": teacher_name}).execute()
        return True
    except Exception as exc:
        st.error(f"Could not add course to Supabase: {exc}")
        return False


def add_mark(supabase, student_id, subject, score, term):
    try:
        supabase.table("marks").insert({"student_id": student_id, "subject": subject, "score": score, "term": term}).execute()
        return True
    except Exception as exc:
        st.error(f"Could not add mark to Supabase: {exc}")
        return False


def register_user(supabase, username, password, role="student", student_id=None, student_data=None):
    if role in {"teacher", "accountant", "principal", "librarian"}:
        st.error("Staff accounts must be created by an administrator")
        return False
    if not username or not password:
        st.error("Username and password are required")
        return False

    existing_user = get_user_by_username(supabase, username)
    if existing_user:
        st.error("That username already exists")
        return False

    try:
        payload = {
            "username": username,
            "password": password,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "admission_no": "",
            "class_name": "",
            "guardian_name": "",
        }
        if student_data:
            payload.update({
                "full_name": student_data.get("full_name", ""),
                "phone": student_data.get("phone", ""),
                "email": student_data.get("email", ""),
            })
            if role == "student":
                payload.update({
                    "admission_no": student_data.get("admission_no", ""),
                    "class_name": student_data.get("class_name", ""),
                    "guardian_name": student_data.get("guardian_name", ""),
                })
        supabase.table(SIGNUP_TABLE).insert(payload).execute()
    except Exception as exc:
        st.error(f"Failed to register user: {exc}")
        return False

    st.session_state.authenticated = True
    st.session_state.current_user = username
    st.session_state.current_role = role
    st.session_state.current_student_id = student_id
    if role in ["admin", "principal"]:
        st.session_state.page = "Dashboard"
    elif role == "teacher":
        st.session_state.page = "Attendance"
    elif role == "accountant":
        st.session_state.page = "Fees"
    elif role == "librarian":
        st.session_state.page = "Library"
    else:
        st.session_state.page = "Student Home"
    st.success("Account created and signed in successfully")
    return True


def login_user(supabase, username, password, role=None):
    seed_default_admin(supabase)
    user = get_user_by_username(supabase, username, role=role)
    if user and user.get("password") == password:
        if role and user.get("role") != role:
            st.error("Invalid login type for this account")
            return False

        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.session_state.current_role = user.get("role")
        st.session_state.current_student_id = user.get("student_id")
        if user.get("role") in ["admin", "principal"]:
            st.session_state.page = "Dashboard"
        elif user.get("role") == "teacher":
            st.session_state.page = "Attendance"
        elif user.get("role") == "accountant":
            st.session_state.page = "Fees"
        elif user.get("role") == "librarian":
            st.session_state.page = "Library"
        else:
            st.session_state.page = "Student Home"
        st.success("Logged in successfully")
        return True

    st.error("Invalid username or password")
    return False


def logout_user():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.current_student_id = None
    st.session_state.page = "Login"
    st.session_state.auth_view = "login"


def render_login_page():
    st.title("🏫 Smart School EMIS")
    st.caption("Sign in to your school account")

    col1, col2, col3 = st.columns(3)
    col1.metric("Students", "100+", "Active")
    col2.metric("Attendance", "98%", "Stable")
    col3.metric("Fee Tracking", "Live", "Smart")

    st.write("")
    col_left, col_right = st.columns([1, 1])
    if col_left.button("Login", use_container_width=True, type="primary"):
        st.session_state.auth_view = "login"
        st.rerun()
    if col_right.button("Create Account", use_container_width=True):
        st.session_state.auth_view = "signup"
        st.rerun()

    supabase = get_supabase_client()
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Admin", "Teacher", "Accountant", "Principal", "Student", "Librarian"]
        )

    with tab1:
        with st.form("admin_login_form"):
            admin_username = st.text_input("Admin Username", key="admin_username")
            admin_password = st.text_input("Admin Password", type="password", key="admin_password")
            submitted = st.form_submit_button("Login as Admin")
            if submitted and login_user(supabase, admin_username, admin_password, role="admin"):
                st.rerun()

    with tab2:
        with st.form("teacher_login_form"):
            teacher_login_username = st.text_input("Username", key="teacher_login_username")
            teacher_login_password = st.text_input("Password", type="password", key="teacher_login_password")
            teacher_login_submitted = st.form_submit_button("Login as Teacher")
            if teacher_login_submitted and login_user(supabase, teacher_login_username, teacher_login_password, role="teacher"):
                st.rerun()

    with tab3:
        with st.form("accountant_login_form"):
            accountant_login_username = st.text_input("Username", key="accountant_login_username")
            accountant_login_password = st.text_input("Password", type="password", key="accountant_login_password")
            accountant_login_submitted = st.form_submit_button("Login as Accountant")
            if accountant_login_submitted and login_user(supabase, accountant_login_username, accountant_login_password, role="accountant"):
                st.rerun()

    with tab4:
        with st.form("principal_login_form"):
            principal_login_username = st.text_input("Username", key="principal_login_username")
            principal_login_password = st.text_input("Password", type="password", key="principal_login_password")
            principal_login_submitted = st.form_submit_button("Login as Principal")
            if principal_login_submitted and login_user(supabase, principal_login_username, principal_login_password, role="principal"):
                st.rerun()

    with tab5:
        with st.form("student_login_form"):
            student_username = st.text_input("Username", key="student_login_username")
            student_password = st.text_input("Password", type="password", key="student_login_password")
            submitted = st.form_submit_button("Login as Student")
            if submitted and login_user(supabase, student_username, student_password, role="student"):
                st.rerun()

    with tab6:
        with st.form("librarian_login_form"):
            librarian_username = st.text_input("Username", key="librarian_login_username")
            librarian_password = st.text_input("Password", type="password", key="librarian_login_password")
            librarian_submitted = st.form_submit_button("Login as Librarian")
            if librarian_submitted and login_user(supabase, librarian_username, librarian_password, role="librarian"):
                st.rerun()

def render_staff_accounts(supabase):
    if st.session_state.get("current_role") != "admin":
        st.error("Only an administrator can create staff accounts.")
        return

    st.title("👥 Staff Accounts")
    tab1, tab2, tab3, tab4 = st.tabs(["Add Teacher", "Add Accountant", "Add Principal", "Add Librarian"])
    with tab1:
        with st.form("admin_add_teacher_account"):
            full_name = st.text_input("Full Name", key="admin_teacher_name")
            subject = st.text_input("Subject", key="admin_teacher_subject")
            phone = st.text_input("Phone", key="admin_teacher_phone")
            email = st.text_input("Email", key="admin_teacher_email")
            username = st.text_input("Username", key="admin_teacher_username")
            password = st.text_input("Password", type="password", key="admin_teacher_password")
            submitted = st.form_submit_button("Create Teacher Account")
            if submitted and full_name and username and password:
                if create_user(supabase, username, password, "teacher", staff_data={"full_name": full_name, "subject": subject, "phone": phone, "email": email}):
                    add_teacher(supabase, full_name, subject, phone, email)
                    st.success("Teacher account created")
    with tab2:
        with st.form("admin_add_accountant_account"):
            full_name = st.text_input("Full Name", key="admin_accountant_name")
            phone = st.text_input("Phone", key="admin_accountant_phone")
            email = st.text_input("Email", key="admin_accountant_email")
            username = st.text_input("Username", key="admin_accountant_username")
            password = st.text_input("Password", type="password", key="admin_accountant_password")
            submitted = st.form_submit_button("Create Accountant Account")
            if submitted:
                if not full_name or not username or not password:
                    st.error("Full name, username, and password are required")
                elif create_user(supabase, username, password, "accountant", staff_data={"full_name": full_name, "phone": phone, "email": email}):
                    st.success("Accountant account created")

    with tab3:
        with st.form("admin_add_principal_account"):
            full_name = st.text_input("Full Name", key="admin_principal_name")
            phone = st.text_input("Phone", key="admin_principal_phone")
            email = st.text_input("Email", key="admin_principal_email")
            username = st.text_input("Username", key="admin_principal_username")
            password = st.text_input("Password", type="password", key="admin_principal_password")
            submitted = st.form_submit_button("Create Principal Account")
            if submitted:
                if not full_name or not username or not password:
                    st.error("Full name, username, and password are required")
                elif create_user(supabase, username, password, "principal", staff_data={"full_name": full_name, "phone": phone, "email": email}):
                    st.success("Principal account created")

    with tab4:
        with st.form("admin_add_librarian_account"):
            full_name = st.text_input("Full Name", key="admin_librarian_name")
            phone = st.text_input("Phone", key="admin_librarian_phone")
            email = st.text_input("Email", key="admin_librarian_email")
            username = st.text_input("Username", key="admin_librarian_username")
            password = st.text_input("Password", type="password", key="admin_librarian_password")
            submitted = st.form_submit_button("Create Librarian Account")
            if submitted:
                if not full_name or not username or not password:
                    st.error("Full name, username, and password are required")
                elif create_user(supabase, username, password, "librarian", staff_data={"full_name": full_name, "phone": phone, "email": email}):
                    st.success("Librarian account created")


def render_signup_page():
    st.title("🏫 Create Your School Account")
    st.caption("Register as a student. Staff accounts are created by an administrator.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Students", "100+", "Active")
    col2.metric("Attendance", "98%", "Stable")
    col3.metric("Fee Tracking", "Live", "Smart")

    st.write("")
    col_left, col_right = st.columns([1, 1])
    if col_left.button("Login", use_container_width=True):
        st.session_state.auth_view = "login"
        st.rerun()
    if col_right.button("Create Account", use_container_width=True, type="primary"):
        st.session_state.auth_view = "signup"
        st.rerun()

    supabase = get_supabase_client()
    tab1, tab2 = st.tabs(["Admin", "Student"])

    with tab1:
        st.info("Admin signup is not available here. Please use the admin login form.")

    with tab2:
        st.info("Teacher, accountant, principal, and librarian accounts must be created from the administrator Staff Accounts page.")
        with st.form("student_signup_form"):
            student_name = st.text_input("Full Name", key="student_signup_name")
            student_admission = st.text_input("Admission Number", key="student_signup_admission")
            student_class = st.text_input("Class", key="student_signup_class")
            guardian_name = st.text_input("Guardian Name", key="student_signup_guardian")
            student_phone = st.text_input("Phone", key="student_signup_phone")
            student_email = st.text_input("Email", key="student_signup_email")
            student_username = st.text_input("Username", key="student_signup_username")
            student_password = st.text_input("Password", type="password", key="student_signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="student_signup_confirm")
            submitted = st.form_submit_button("Register as Student")
            if submitted:
                if student_password != confirm_password:
                    st.error("Passwords do not match")
                elif not student_name or not student_admission or not student_class or not student_username:
                    st.error("Name, admission number, class, and username are required")
                else:
                    student_data = {
                        "full_name": student_name,
                        "admission_no": student_admission,
                        "class_name": student_class,
                        "guardian_name": guardian_name,
                        "phone": student_phone,
                        "email": student_email,
                        "created_at": datetime.now().isoformat(),
                    }
                    student_id = None
                    try:
                        response = supabase.table("students").insert(student_data).execute()
                        if response.data:
                            student_id = response.data[0].get("id")
                    except Exception as exc:
                        st.error(f"Could not create the student record: {exc}")

                    if student_id and register_user(
                        supabase,
                        student_username,
                        student_password,
                        role="student",
                        student_id=student_id,
                        student_data=student_data,
                    ):
                        st.rerun()

def render_dashboard(students, attendance_records, fee_records, marks, teachers, courses):
    st.title("📊 Smart Dashboard")
    total_students = len(students)
    attendance_present = sum(1 for entry in attendance_records if entry.get("status") == "Present")
    attendance_absent = len(attendance_records) - attendance_present
    pending_fees = sum(float(entry.get("amount", 0)) for entry in fee_records if entry.get("status") == "Pending")
    average_score = round(sum(int(entry.get("score", 0)) for entry in marks) / len(marks), 1) if marks else 0
    attendance_rate = round(attendance_present / max(1, attendance_present + attendance_absent) * 100, 1) if (attendance_present + attendance_absent) else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Students", total_students)
    col2.metric("Present", attendance_present)
    col3.metric("Absent", attendance_absent)
    col4.metric("Attendance %", f"{attendance_rate}%")
    col5.metric("Pending Fees", f"{pending_fees:,.0f}")
    col6.metric("Avg Score", average_score)

    chart_df = pd.DataFrame({
        "Metric": ["Students", "Present", "Absent", "Pending Fees"],
        "Value": [total_students, attendance_present, attendance_absent, pending_fees],
    })
    st.subheader("Overview Chart")
    st.bar_chart(chart_df.set_index("Metric"), use_container_width=True)

    st.subheader("Smart Insights")
    if pending_fees > 0:
        st.warning("Fee collection needs attention; several students still have pending dues.")
    if attendance_absent > 0:
        st.info("Attendance review is recommended for the latest records.")
    if teachers and courses:
        st.success("Your school operations are active with teachers and classes already configured.")

    st.subheader("Recent Student Activity")
    recent_students = pd.DataFrame(students[:5])
    if not recent_students.empty:
        st.dataframe(recent_students[["admission_no", "full_name", "class_name", "email"]], use_container_width=True)
    else:
        st.info("No student activity yet")


def render_students(students, supabase, can_edit=True):
    st.title("🧑‍🎓 Students")
    if can_edit:
        with st.form("student_form"):
            full_name = st.text_input("Full Name")
            admission_no = st.text_input("Admission Number")
            class_name = st.text_input("Class")
            guardian_name = st.text_input("Guardian Name")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Add Student")
            if submitted:
                if not full_name or not admission_no or not class_name:
                    st.error("Full name, admission number, and class are required")
                else:
                    student_data = {
                        "full_name": full_name,
                        "admission_no": admission_no,
                        "class_name": class_name,
                        "guardian_name": guardian_name,
                        "phone": phone,
                        "email": email,
                        "created_at": datetime.now().isoformat(),
                    }
                    if add_student(supabase, student_data):
                        st.rerun()

    st.subheader("Student List")
    if students:
        student_df = pd.DataFrame(students)[["id", "admission_no", "full_name", "class_name", "guardian_name", "phone", "email"]]
        st.dataframe(student_df, use_container_width=True)

        if not can_edit:
            return

        st.markdown("---")
        st.subheader("Update or Delete Student")
        student_options = {f"{student['id']} - {student['full_name']}": student for student in students}
        selected_label = st.selectbox("Select Student to Manage", list(student_options.keys()), key="manage_student_select")
        selected_student = student_options[selected_label]

        full_name = st.text_input("Full Name", value=selected_student.get("full_name", ""), key=f"edit_full_name_{selected_student['id']}")
        admission_no = st.text_input("Admission Number", value=selected_student.get("admission_no", ""), key=f"edit_admission_no_{selected_student['id']}")
        class_name = st.text_input("Class", value=selected_student.get("class_name", ""), key=f"edit_class_name_{selected_student['id']}")
        guardian_name = st.text_input("Guardian Name", value=selected_student.get("guardian_name", ""), key=f"edit_guardian_name_{selected_student['id']}")
        phone = st.text_input("Phone", value=selected_student.get("phone", ""), key=f"edit_phone_{selected_student['id']}")
        email = st.text_input("Email", value=selected_student.get("email", ""), key=f"edit_email_{selected_student['id']}")

        col1, col2 = st.columns(2)
        if col1.button("Update Student", key=f"update_student_{selected_student['id']}"):
            if not full_name or not admission_no or not class_name:
                st.error("Full name, admission number, and class are required")
            else:
                updated_data = {
                    "full_name": full_name,
                    "admission_no": admission_no,
                    "class_name": class_name,
                    "guardian_name": guardian_name,
                    "phone": phone,
                    "email": email,
                }
                if update_student(supabase, selected_student["id"], updated_data):
                    st.rerun()

        if col2.button("Delete Student", type="secondary", key=f"delete_student_{selected_student['id']}"):
            if delete_student(supabase, selected_student["id"]):
                st.rerun()
    else:
        st.info("No students available")


def render_student_details(students, attendance_records, marks, supabase, can_edit=True):
    st.title("🧑‍🎓 Student Details & Marks")
    if students:
        student_names = {student["full_name"]: student for student in students}
        selected_name = st.selectbox("Select Student", list(student_names.keys()))
        student = student_names[selected_name]
        st.subheader(student["full_name"])
        st.write(f"Admission No: {student.get('admission_no')}")
        st.write(f"Class: {student.get('class_name')}")
        st.write(f"Guardian: {student.get('guardian_name')}")
        st.write(f"Phone: {student.get('phone')}")
        st.write(f"Email: {student.get('email')}")

        student_marks = [mark for mark in marks if mark.get("student_id") == student["id"]]
        student_attendance = [entry for entry in attendance_records if entry.get("student_id") == student["id"]]
        avg_score = round(sum(int(mark.get("score", 0)) for mark in student_marks) / len(student_marks), 1) if student_marks else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Attendance", len(student_attendance))
        col2.metric("Marks Added", len(student_marks))
        col3.metric("Average Score", avg_score)

        if can_edit:
            with st.form("marks_form"):
                subject = st.text_input("Subject")
                score = st.number_input("Score", min_value=0, max_value=100, step=1)
                term = st.text_input("Term")
                submitted = st.form_submit_button("Add Mark")
                if submitted and subject and term:
                    if add_mark(supabase, student["id"], subject, score, term):
                        st.rerun()

        st.subheader("Marks")
        if student_marks:
            marks_df = pd.DataFrame(student_marks)
            st.dataframe(marks_df[["subject", "score", "term"]], use_container_width=True)
        else:
            st.info("No marks recorded yet")
    else:
        st.info("No students to display")


def render_attendance(students, attendance_records, supabase, can_edit=True):
    st.title("📝 Attendance")
    if not students:
        st.info("Add students first")
        return

    present_count = sum(1 for entry in attendance_records if entry.get("status") == "Present")
    absent_count = sum(1 for entry in attendance_records if entry.get("status") == "Absent")
    late_count = sum(1 for entry in attendance_records if entry.get("status") == "Late")

    col1, col2, col3 = st.columns(3)
    col1.metric("Present", present_count)
    col2.metric("Absent", absent_count)
    col3.metric("Late", late_count)

    class_names = sorted({student.get("class_name", "Unassigned") for student in students})
    selected_class = st.selectbox("Choose Class", class_names, key="attendance_class")
    class_students = [student for student in students if student.get("class_name", "Unassigned") == selected_class]

    st.subheader(f"Students in {selected_class}")
    student_list = pd.DataFrame(
        [
            {
                "id": student.get("id"),
                "full_name": student.get("full_name"),
                "admission_no": student.get("admission_no"),
                "class_name": student.get("class_name"),
            }
            for student in class_students
        ]
    )
    if not student_list.empty:
        st.dataframe(student_list, use_container_width=True, hide_index=True)

    if class_students:
        student_options = {
            f"{student.get('full_name')} ({student.get('admission_no')})": student
            for student in class_students
        }
        selected_name = st.selectbox("Open Student Attendance", list(student_options.keys()), key="attendance_student")
        selected_student = student_options[selected_name]
        selected_student_id = selected_student.get("id")
        selected_records = [
            record for record in attendance_records
            if str(record.get("student_id")) == str(selected_student_id)
        ]
        st.subheader(f"Attendance: {selected_student.get('full_name')}")
        if selected_records:
            st.dataframe(
                pd.DataFrame(selected_records)[["attendance_date", "status"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No attendance records for this student")

    if can_edit and class_students:
        attendance_date = st.date_input("Attendance Date", value=date.today(), key="attendance_date")
        status = st.selectbox("Status", ["Present", "Absent", "Late"], key="attendance_status")

        if st.button("Mark Attendance"):
            if add_attendance(supabase, selected_student_id, attendance_date, status):
                st.success("Attendance recorded")
                st.rerun()

    st.subheader("Attendance Records")
    if attendance_records:
        df = pd.DataFrame(attendance_records)
        st.dataframe(df[["attendance_date", "student_id", "status"]], use_container_width=True, hide_index=True)
    else:
        st.info("No attendance records yet")


def render_courses(courses, supabase, can_edit=True):
    st.title("📚 Courses")
    if can_edit:
        with st.form("course_form"):
            course_name = st.text_input("Course Name")
            class_name = st.text_input("Class")
            teacher_name = st.text_input("Teacher Name")
            submitted = st.form_submit_button("Add Course")
            if submitted and course_name and class_name:
                if add_course(supabase, course_name, class_name, teacher_name):
                    st.rerun()

    st.subheader("Course List")
    if courses:
        st.dataframe(pd.DataFrame(courses), use_container_width=True)
    else:
        st.info("No courses created yet")


def render_fees(students, fee_records, supabase, can_edit=True):
    st.title("💰 Fees")
    def calculate_fee_summary(records):
        paid = sum(float(record.get("amount", 0) or 0) for record in records if record.get("status") == "Paid")
        due = sum(float(record.get("amount", 0) or 0) for record in records if record.get("status") in {"Pending", "Overdue"})
        advance = max(paid - due, 0)
        return due + paid, due, paid, advance

    total_fee, due_total, paid_total, advance_total = calculate_fee_summary(fee_records)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Fee", f"{total_fee:,.0f}")
    col2.metric("Due Fee", f"{due_total:,.0f}")
    col3.metric("Paid Fee", f"{paid_total:,.0f}")
    col4.metric("Advance", f"{advance_total:,.0f}")

    if students and can_edit:
        fee_student_options = {student["full_name"]: student["id"] for student in students}
        selected_fee_name = st.selectbox("Select Student", list(fee_student_options.keys()), key="fee_student")
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        payment_date = st.date_input("Payment Date", value=date.today(), key="fee_date")
        status = st.selectbox("Status", ["Paid", "Pending", "Overdue"], key="fee_status")
        note = st.text_area("Note")
        selected_student_records = [
            record for record in fee_records
            if str(record.get("student_id")) == str(fee_student_options[selected_fee_name])
        ]
        preview_records = [*selected_student_records, {"amount": amount, "status": status}]
        preview_total, preview_due, preview_paid, preview_advance = calculate_fee_summary(preview_records)
        st.caption(
            f"Live preview: Total {preview_total:,.2f} | Due {preview_due:,.2f} | "
            f"Paid {preview_paid:,.2f} | Advance {preview_advance:,.2f}"
        )
        if st.button("Save Fee Record"):
            if add_fee_record(supabase, fee_student_options[selected_fee_name], amount, payment_date, status, note):
                st.rerun()
    else:
        st.info("Add students first")

    st.subheader("Fee Records")
    if fee_records:
        fee_df = pd.DataFrame(fee_records)
        st.dataframe(fee_df, use_container_width=True, hide_index=True)
        receipt_student_options = {
            f"{student.get('full_name')} ({student.get('admission_no')})": student
            for student in students
            if any(str(record.get("student_id")) == str(student.get("id")) for record in fee_records)
        }
        if receipt_student_options:
            selected_receipt_label = st.selectbox("Select Student Receipt", list(receipt_student_options), key="fee_receipt_student")
            selected_receipt_student = receipt_student_options[selected_receipt_label]
            selected_receipt_records = [
                record for record in fee_records
                if str(record.get("student_id")) == str(selected_receipt_student.get("id"))
            ]
            receipt_total = sum(float(record.get("amount", 0)) for record in selected_receipt_records)
            receipt_paid = sum(float(record.get("amount", 0)) for record in selected_receipt_records if record.get("status") == "Paid")
            receipt_due = sum(float(record.get("amount", 0)) for record in selected_receipt_records if record.get("status") in {"Pending", "Overdue"})
            receipt_advance = max(receipt_paid - receipt_due, 0)
            receipt_rows = "".join(
                f"<tr><td>{html.escape(str(record.get('payment_date', '')))}</td>"
                f"<td>{html.escape(str(record.get('status', '')))}</td>"
                f"<td>{float(record.get('amount', 0)):,.2f}</td></tr>"
                for record in selected_receipt_records
            )
            receipt_html = f"""
            <button onclick="printFeeReceipt()" style="padding:11px 18px;cursor:pointer;background:#c8a45d;color:#17130b;border:0;border-radius:6px;font-weight:700">Print Fee Receipt</button>
            <script>
            function printFeeReceipt() {{
                const receipt = document.getElementById('fee-receipt').outerHTML;
                const styles = document.getElementById('fee-receipt-styles').innerHTML;
                const printWindow = window.open('', '_blank', 'noopener,noreferrer,width=900,height=700') || window.parent.open('', '_blank');
                if (!printWindow) {{
                    window.print();
                    return;
                }}
                printWindow.document.write('<html><head><title>School Fee Receipt</title><style>' + styles + '</style></head><body>' + receipt + '</body></html>');
                printWindow.document.close();
                printWindow.onload = () => setTimeout(() => printWindow.print(), 250);
            }}
            </script>
            <style id="fee-receipt-styles">
                body {{ margin:0; background:#eeeae2; font-family:Arial,sans-serif; color:#25231f; }}
                .invoice {{ max-width:760px; margin:20px auto; background:#fff; padding:42px; box-shadow:0 8px 30px #bbb; }}
                .brand {{ display:flex; justify-content:space-between; align-items:flex-start; border-bottom:3px solid #c8a45d; padding-bottom:20px; }}
                .brand h1 {{ margin:0; font-family:Georgia,serif; font-size:30px; letter-spacing:1px; }}
                .brand p {{ margin:6px 0 0; color:#7b756b; }}
                .receipt-label {{ text-align:right; color:#9b7938; font-weight:700; letter-spacing:2px; text-transform:uppercase; }}
                .meta {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:26px 0; color:#555; }}
                .meta strong {{ color:#222; display:block; margin-top:3px; }}
                table {{ width:100%; border-collapse:collapse; margin-top:20px; }}
                th {{ background:#25231f; color:#fff; text-align:left; padding:12px; font-size:12px; text-transform:uppercase; letter-spacing:1px; }}
                td {{ padding:13px 12px; border-bottom:1px solid #e5e0d7; }}
                td:last-child, th:last-child {{ text-align:right; }}
                .totals {{ margin:24px 0 0 auto; max-width:300px; }}
                .totals div {{ display:flex; justify-content:space-between; padding:7px 0; }}
                .grand {{ border-top:2px solid #c8a45d; font-size:18px; font-weight:700; padding-top:12px !important; }}
                .footer {{ margin-top:38px; color:#8a847a; font-size:12px; text-align:center; }}
                @media print {{ body {{ background:#fff; }} .invoice {{ margin:0; box-shadow:none; max-width:none; }} }}
            </style>
            <div id="fee-receipt" class="invoice">
                <div class="brand"><div><h1>Altaff Academy</h1><p>School Management Information System</p></div><div class="receipt-label">Fee Receipt</div></div>
                <div class="meta"><div>Student<strong>{html.escape(str(selected_receipt_student.get('full_name', '')))}</strong></div><div>Admission No<strong>{html.escape(str(selected_receipt_student.get('admission_no', '')))}</strong></div></div>
                <table><tr><th>Date</th><th>Status</th><th>Amount</th></tr>{receipt_rows}</table>
                <div class="totals"><div><span>Total Fee</span><strong>{receipt_total:,.2f}</strong></div><div><span>Paid</span><strong>{receipt_paid:,.2f}</strong></div><div><span>Advance</span><strong>{receipt_advance:,.2f}</strong></div><div class="grand"><span>Due</span><strong>{receipt_due:,.2f}</strong></div></div>
                <div class="footer">Thank you for choosing Altaff Academy</div>
            </div>
            """
            components.html(receipt_html, height=360, scrolling=True)
    else:
        st.info("No fee records yet")


def render_teachers(teachers, supabase, can_edit=True):
    st.title("👩‍🏫 Teachers")
    if can_edit:
        with st.form("teacher_form"):
            full_name = st.text_input("Teacher Name")
            subject = st.text_input("Subject")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Add Teacher")
            if submitted and full_name:
                if add_teacher(supabase, full_name, subject, phone, email):
                    st.rerun()

    st.subheader("Teacher List")
    if teachers:
        st.dataframe(pd.DataFrame(teachers), use_container_width=True)
    else:
        st.info("No teachers added yet")


def render_reports(students, attendance_records, fee_records, marks):
    st.title("📈 Reports & Analytics")
    if marks:
        marks_df = pd.DataFrame(marks)
        st.subheader("Average Scores by Subject")
        st.bar_chart(marks_df.groupby("subject")["score"].mean(), use_container_width=True)
    else:
        st.info("No marks yet")

    pending = [record for record in fee_records if record.get("status") == "Pending"]
    st.subheader("Pending Fees")
    if pending:
        st.dataframe(pd.DataFrame(pending)[["student_id", "amount", "payment_date", "note"]], use_container_width=True)
    else:
        st.info("No pending fees")

    st.subheader("Attendance Summary")
    if attendance_records:
        st.dataframe(pd.DataFrame(attendance_records)[["attendance_date", "student_id", "status"]], use_container_width=True)
    else:
        st.info("No attendance data")


def render_library(books, loans, students, supabase, can_edit=True, can_manage_fines=False):
    st.title("📖 Library")
    if can_edit:
        with st.expander("Add Book"):
            with st.form("library_book_form"):
                title = st.text_input("Title")
                author = st.text_input("Author")
                isbn = st.text_input("ISBN")
                copies = st.number_input("Total Copies", min_value=1, step=1)
                submitted = st.form_submit_button("Add Book")
                if submitted and title:
                    if save_record(
                        supabase,
                        "library_books",
                        {
                            "title": title,
                            "author": author,
                            "isbn": isbn,
                            "total_copies": copies,
                            "available_copies": copies,
                            "created_at": datetime.now().isoformat(),
                        },
                    ):
                        st.rerun()

    st.subheader("Book Catalogue")
    if books:
        st.dataframe(pd.DataFrame(books)[["id", "title", "author", "isbn", "total_copies", "available_copies"]], use_container_width=True)
    else:
        st.info("No books added yet")

    if can_edit and books and students:
        st.subheader("Issue Book")
        available_books = [book for book in books if int(book.get("available_copies", 0)) > 0]
        if available_books:
            book_options = {f"{book['title']} ({book['available_copies']} available)": book for book in available_books}
            student_options = {student["full_name"]: student for student in students}
            selected_book = st.selectbox("Book", list(book_options), key="issue_book")
            selected_student = st.selectbox("Student", list(student_options), key="issue_student")
            due_date = st.date_input("Due Date", value=date.today(), key="issue_due_date")
            if st.button("Issue Book"):
                book = book_options[selected_book]
                student = student_options[selected_student]
                if save_record(
                    supabase,
                    "library_loans",
                    {
                        "book_id": book["id"],
                        "student_id": student["id"],
                        "issue_date": str(date.today()),
                        "due_date": str(due_date),
                        "status": "Issued",
                        "fine_amount": 0,
                        "created_at": datetime.now().isoformat(),
                    },
                ) and update_record(
                    supabase,
                    "library_books",
                    book["id"],
                    {"available_copies": int(book["available_copies"]) - 1},
                ):
                    st.rerun()
        else:
            st.info("All books are currently issued")

    st.subheader("Loans and Fine Management")
    if loans:
        loan_df = pd.DataFrame(loans)
        st.dataframe(loan_df, use_container_width=True)
        active_loans = [loan for loan in loans if loan.get("status") != "Returned"]
        if not can_edit:
            active_loans = []
        if active_loans:
            loan_options = {f"Loan {loan['id']} - Book {loan['book_id']} / Student {loan['student_id']}": loan for loan in active_loans}
            selected_loan_label = st.selectbox("Loan to return", list(loan_options), key="return_loan")
            if st.button("Return Book"):
                loan = loan_options[selected_loan_label]
                book = next((item for item in books if item.get("id") == loan.get("book_id")), None)
                updated = update_record(
                    supabase,
                    "library_loans",
                    loan["id"],
                    {"return_date": str(date.today()), "status": "Returned"},
                )
                if updated and book:
                    updated = update_record(
                        supabase,
                        "library_books",
                        book["id"],
                        {"available_copies": int(book["available_copies"]) + 1},
                    )
                if updated:
                    st.rerun()
    else:
        st.info("No loans yet")

    if can_manage_fines and loans:
        st.subheader("Fine Management")
        fine_options = {f"Loan {loan['id']} / Student {loan['student_id']}": loan for loan in loans}
        selected_fine_label = st.selectbox("Select Loan", list(fine_options), key="fine_loan")
        selected_fine_loan = fine_options[selected_fine_label]
        fine_amount = st.number_input(
            "Fine Amount",
            min_value=0.0,
            value=float(selected_fine_loan.get("fine_amount", 0) or 0),
            step=10.0,
            key="fine_amount",
        )
        if st.button("Save Fine"):
            if update_record(supabase, "library_loans", selected_fine_loan["id"], {"fine_amount": fine_amount}):
                st.success("Fine saved")
                st.rerun()

    if can_manage_fines and loans:
        student_by_id = {str(student.get("id")): student for student in students}
        book_by_id = {str(book.get("id")): book for book in books}
        fine_total = sum(float(loan.get("fine_amount", 0) or 0) for loan in loans)
        bill_rows = "".join(
            f"<tr><td>{html.escape(str(student_by_id.get(str(loan.get('student_id')), {}).get('full_name', loan.get('student_id', ''))))}</td>"
            f"<td>{html.escape(str(book_by_id.get(str(loan.get('book_id')), {}).get('title', loan.get('book_id', ''))))}</td>"
            f"<td>{html.escape(str(loan.get('issue_date', '')))}</td>"
            f"<td>{html.escape(str(loan.get('return_date') or loan.get('due_date', '')))}</td>"
            f"<td>{html.escape(str(loan.get('status', '')))}</td>"
            f"<td>{float(loan.get('fine_amount', 0) or 0):,.2f}</td></tr>"
            for loan in loans
        )
        fine_bill_html = f"""
        <button onclick="printFineReceipt()" style="padding:11px 18px;cursor:pointer;background:#c8a45d;color:#17130b;border:0;border-radius:6px;font-weight:700">Print Fine Receipt</button>
        <script>
        function printFineReceipt() {{
            const receipt = document.getElementById('fine-receipt').outerHTML;
            const styles = document.getElementById('fine-receipt-styles').innerHTML;
            const printWindow = window.open('', '_blank', 'noopener,noreferrer,width=900,height=700') || window.parent.open('', '_blank');
            if (!printWindow) {{
                window.print();
                return;
            }}
            printWindow.document.write('<html><head><title>Library Fine Receipt</title><style>' + styles + '</style></head><body>' + receipt + '</body></html>');
            printWindow.document.close();
            printWindow.onload = () => setTimeout(() => printWindow.print(), 250);
        }}
        </script>
        <style id="fine-receipt-styles">
            body {{ margin:0; background:#eeeae2; font-family:Arial,sans-serif; color:#25231f; }}
            .invoice {{ max-width:760px; margin:20px auto; background:#fff; padding:42px; box-shadow:0 8px 30px #bbb; }}
            .brand {{ display:flex; justify-content:space-between; align-items:flex-start; border-bottom:3px solid #c8a45d; padding-bottom:20px; }}
            .brand h1 {{ margin:0; font-family:Georgia,serif; font-size:30px; letter-spacing:1px; }}
            .brand p {{ margin:6px 0 0; color:#7b756b; }}
            .receipt-label {{ text-align:right; color:#9b7938; font-weight:700; letter-spacing:2px; text-transform:uppercase; }}
            .meta {{ margin:26px 0; color:#555; }}
            .meta strong {{ color:#222; display:block; margin-top:3px; }}
            table {{ width:100%; border-collapse:collapse; margin-top:20px; }}
            th {{ background:#25231f; color:#fff; text-align:left; padding:12px 9px; font-size:11px; text-transform:uppercase; letter-spacing:.7px; }}
            td {{ padding:13px 9px; border-bottom:1px solid #e5e0d7; }}
            td:last-child, th:last-child {{ text-align:right; }}
            .grand {{ margin:24px 0 0 auto; max-width:300px; border-top:2px solid #c8a45d; display:flex; justify-content:space-between; padding-top:12px; font-size:18px; font-weight:700; }}
            .footer {{ margin-top:38px; color:#8a847a; font-size:12px; text-align:center; }}
            @media print {{ body {{ background:#fff; }} .invoice {{ margin:0; box-shadow:none; max-width:none; }} }}
        </style>
        <div id="fine-receipt" class="invoice">
            <div class="brand"><div><h1>Altaff Academy</h1><p>School Management Information System</p></div><div class="receipt-label">Fine Receipt</div></div>
            <div class="meta">Generated<strong>{html.escape(str(date.today()))}</strong></div>
            <table><tr><th>Student</th><th>Book</th><th>Issued</th><th>Returned/Due</th><th>Status</th><th>Fine</th></tr>{bill_rows}</table>
            <div class="grand"><span>Total Fine</span><strong>{fine_total:,.2f}</strong></div>
            <div class="footer">Library circulation record</div>
        </div>
        """
        components.html(fine_bill_html, height=390, scrolling=True)


def render_student_home(students, attendance_records, fee_records, marks, books, loans, supabase):
    st.title("🎓 Student Dashboard")
    st.write(f"Welcome, {st.session_state.current_user}")
    student_id = st.session_state.current_student_id
    student = next((s for s in students if s.get("id") == student_id), None)

    if student:
        st.subheader(student.get("full_name"))
        st.write(f"Admission No: {student.get('admission_no')}")
        st.write(f"Class: {student.get('class_name')}")
        st.write(f"Guardian: {student.get('guardian_name')}")
        st.write(f"Phone: {student.get('phone')}")
        st.write(f"Email: {student.get('email')}")

    student_attendance = [record for record in attendance_records if record.get("student_id") == student_id]
    student_marks = [record for record in marks if record.get("student_id") == student_id]
    student_fees = [record for record in fee_records if record.get("student_id") == student_id]
    student_loans = [record for record in loans if record.get("student_id") == student_id]

    if student_attendance:
        st.subheader("Your Attendance")
        st.dataframe(pd.DataFrame(student_attendance)[["attendance_date", "status"]], use_container_width=True)
    if student_marks:
        st.subheader("Your Marks")
        st.dataframe(pd.DataFrame(student_marks)[["subject", "score", "term"]], use_container_width=True)
    if student_fees:
        st.subheader("Your Fee Records")
        st.dataframe(pd.DataFrame(student_fees)[["payment_date", "amount", "status", "note"]], use_container_width=True)
    st.subheader("Library Books")
    if books:
        st.dataframe(pd.DataFrame(books)[["title", "author", "available_copies"]], use_container_width=True)
    else:
        st.info("No library books available")
    if student_loans:
        st.subheader("Your Library Loans")
        st.dataframe(pd.DataFrame(student_loans)[["book_id", "issue_date", "due_date", "status", "fine_amount"]], use_container_width=True)

    if st.button("Logout"):
        logout_user()
        st.rerun()


def main():
    ensure_state()
    supabase = get_supabase_client()

    if not st.session_state.authenticated:
        if st.session_state.auth_view == "signup":
            render_signup_page()
        else:
            render_login_page()
        return

    st.sidebar.title("School EMIS")
    st.sidebar.write(f"Signed in as: {st.session_state.current_user} ({st.session_state.current_role})")

    if st.session_state.current_role == "admin":
        page_options = ["Staff Accounts", "Courses", "Logout"]
    elif st.session_state.current_role == "principal":
        page_options = ["Dashboard", "Students", "Attendance", "Student Details & Marks", "Courses", "Fees", "Teachers", "Reports", "Library", "Logout"]
    elif st.session_state.current_role == "teacher":
        page_options = ["Attendance", "Logout"]
    elif st.session_state.current_role == "accountant":
        page_options = ["Fees", "Students", "Library", "Logout"]
    elif st.session_state.current_role == "librarian":
        page_options = ["Library", "Logout"]
    else:
        page_options = ["Student Home", "Logout"]

    page = st.sidebar.radio("Navigation", page_options, index=0)
    st.session_state.page = page

    students = load_students(supabase)
    attendance_records = load_attendance(supabase)
    fee_records = load_fee_records(supabase)
    courses = load_courses(supabase)
    marks = load_marks(supabase)
    teachers = load_teachers(supabase)
    books = load_library_books(supabase)
    loans = load_library_loans(supabase)

    if page == "Staff Accounts":
        render_staff_accounts(supabase)
    elif page == "Dashboard":
        render_dashboard(students, attendance_records, fee_records, marks, teachers, courses)
    elif page == "Students":
        render_students(students, supabase, can_edit=st.session_state.current_role in {"accountant"})
    elif page == "Attendance":
        render_attendance(students, attendance_records, supabase, can_edit=st.session_state.current_role == "teacher")
    elif page == "Student Details & Marks":
        render_student_details(students, attendance_records, marks, supabase, can_edit=st.session_state.current_role == "accountant")
    elif page == "Courses":
        render_courses(courses, supabase, can_edit=st.session_state.current_role == "admin")
    elif page == "Fees":
        render_fees(students, fee_records, supabase, can_edit=st.session_state.current_role == "accountant")
    elif page == "Teachers":
        render_teachers(teachers, supabase, can_edit=False)
    elif page == "Reports":
        render_reports(students, attendance_records, fee_records, marks)
    elif page == "Student Home":
        render_student_home(students, attendance_records, fee_records, marks, books, loans, supabase)
    elif page == "Library":
        render_library(
            books,
            loans,
            students,
            supabase,
            can_edit=st.session_state.current_role == "librarian",
            can_manage_fines=st.session_state.current_role == "accountant",
        )
    elif page == "Logout":
        render_logout_page()


def render_logout_page():
    st.title("🚪 Logout")
    st.write("You are about to sign out of the EMIS dashboard.")
    if st.button("Logout"):
        logout_user()
        st.rerun()


if __name__ == "__main__":
    main()
