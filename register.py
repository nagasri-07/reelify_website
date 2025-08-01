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

# --- Check if email exists ---
def check_email_exists(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
            return cur.fetchone() is not None

# --- Register user ---
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
    return True, "✅ Registration successful!"

# --- Get stored hash for login ---
def get_user_password_hash(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
            result = cur.fetchone()
            return result[0] if result else None

# --- Streamlit UI ---
st.set_page_config(page_title="Login & Register")
st.title("🔐 Authentication App")

# Optional table creation
if st.sidebar.button("📦 Create Users Table"):
    create_users_table()
    st.sidebar.success("✅ Users table created successfully!")

# --- Switch between Login & Register ---
mode = st.radio("Choose Mode", ["Login", "Register"])

# --- Already Logged In? ---
if 'user' in st.session_state:
    st.success(f"✅ Logged in as: {st.session_state['user']}")
    if st.button("Logout"):
        del st.session_state['user']
        st.experimental_rerun()
else:
    if mode == "Register":
        st.subheader("📝 Register New User")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            if name and email and password:
                success, msg = register_user(name, email, password)
                st.success(msg) if success else st.error(msg)
            else:
                st.warning("Please fill out all fields.")

    else:  # Login
        st.subheader("🔑 User Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Login"):
            stored_hash = get_user_password_hash(email)
            if stored_hash and bcrypt.checkpw(password.encode(), stored_hash.encode()):
                st.session_state['user'] = email
                st.success("🎉 Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Invalid email or password")
