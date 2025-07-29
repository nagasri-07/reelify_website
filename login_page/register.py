import streamlit as st
import bcrypt
import psycopg2
from psycopg2 import sql

# --- Database Connection ---
def get_connection():
    return psycopg2.connect(
        dbname="your_db",
        user="your_user",
        password="your_password",
        host="localhost",
        port="5432"
    )

# --- Password Hashing ---
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_email_exists(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

def register_user(name, email, password):
    if check_email_exists(email):
        return False, "Email already registered."

    hashed = hash_password(password)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            conn.commit()
    return True, "Registration successful!"

# --- Streamlit UI ---
st.title("📝 Register New User")

with st.form("register_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Register")

    if submit:
        if not name or not email or not password:
            st.warning("Please fill all fields.")
        else:
            success, msg = register_user(name, email, password)
            if success:
                st.success(msg)
            else:
                st.error(msg)
