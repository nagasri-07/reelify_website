import streamlit as st
import psycopg2
import bcrypt

# --- PostgreSQL Connection ---
def get_connection():
    return psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="npg_Rpc87HaPXQAt",
        host="ep-rapid-rain-a195g7cp-pooler.ap-southeast-1.aws.neon.tech",
        port="5432",
        sslmode="require"
    )

# --- Create Users Table (Optional) ---
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

# --- Email Check ---
def check_email_exists(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

# --- Register User ---
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

# --- Streamlit UI ---
st.set_page_config(page_title="User Registration")
st.title("📝 Register New User")

# Optional table creation
if st.sidebar.button("Create Users Table"):
    create_users_table()
    st.sidebar.success("Users table created successfully!")

name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Register"):
    if name and email and password:
        success, msg = register_user(name, email, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)
    else:
        st.warning("Please fill out all fields.")
