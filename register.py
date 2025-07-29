import streamlit as st
import bcrypt
import psycopg2
from psycopg2 import sql

# --- Streamlit UI Setup ---
st.set_page_config(page_title="User Registration")
st.title("📝 Register New User")

# --- Optional: Table Creation (only runs if checkbox is checked) ---
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
    st.success("✅ Users table ensured.")

# --- Database Connection ---
def get_connection():
    return psycopg2.connect(
        dbname="your_db",         # 🔁 Replace with actual DB name
        user="your_user",         # 🔁 Replace with DB username
        password="your_password", # 🔁 Replace with DB password
        host="localhost",         # 🔁 For Streamlit Cloud, use a remote DB host
        port="5432"
    )

# --- Password Hashing ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# --- Check if email already exists ---
def check_email_exists(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

# --- Register new user ---
def register_user(name, email, password):
    if check_email_exists(email):
        return False, "⚠️ Email already registered."

    hashed = hash_password(password)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            conn.commit()
    return True, "🎉 Registration successful!"

# --- Optional: Create Table Checkbox ---
if st.checkbox("Create users table in database"):
    create_users_table()

# --- Registration Form ---
with st.form("register_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Register")

    if submit:
        if not name or not email or not password:
            st.warning("Please fill all fields.")
        else:
            try:
                success, msg = register_user(name, email, password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("🔐 Secure registration using PostgreSQL + bcrypt")
