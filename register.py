import streamlit as st
import psycopg2
import bcrypt

# --- Cached DB Connection ---
@st.cache_resource(show_spinner=False)
def get_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_Rpc87HaPXQAt",
        host="ep-rapid-rain-a195g7cp-pooler.ap-southeast-1.aws.neon.tech",
        port="5432",
        sslmode="require"
    )

# --- Create Users Table ---
def create_users_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                );
            """)
            conn.commit()

# --- Helper Functions ---
def check_email_exists(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

def register_user(name, email, password):
    if check_email_exists(email):
        return False, "Email already registered."

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed_pw)
            )
            conn.commit()
    return True, "Registration successful!"

def login_user(email, password):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            if result and bcrypt.checkpw(password.encode(), result[0].encode()):
                return True
    return False

# --- UI Setup ---
st.set_page_config(page_title="Auth App", page_icon="🔐")
st.title("🔐 Login & Registration")

menu = st.sidebar.radio("Select", ["Register", "Login", "Dashboard"])
if st.sidebar.button("Create Users Table"):
    create_users_table()
    st.sidebar.success("Users table created!")

# --- Registration Page ---
if menu == "Register":
    st.subheader("📝 Register New User")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if name and email and password:
            success, msg = register_user(name, email, password)
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please fill out all fields.")

# --- Login Page ---
elif menu == "Login":
    st.subheader("🔑 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if login_user(email, password):
            st.session_state['user'] = email
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials.")

# --- Dashboard Page ---
elif menu == "Dashboard":
    st.subheader("📋 Dashboard")
    user = st.session_state.get("user")

    if user:
        st.success(f"Welcome, {user}!")
        if st.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()
    else:
        st.warning("Please login first.")
