import streamlit as st
import psycopg2
import bcrypt
import google.generativeai as genai
import tempfile
import subprocess
import os
import whisper
import re

# --- CONFIGURE GEMINI ---
API_KEY = "AIzaSyDou_lfKmdoC19dqpolzGY6EY7eUskkgUI"
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-pro")

# --- DB Connection ---
def get_connection():
    try:
        return psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_Rpc87HaPXQAt",
            host="ep-rapid-rain-a195g7cp-pooler.ap-southeast-1.aws.neon.tech",
            port="5432",
            sslmode="require"
        )
    except psycopg2.OperationalError:
        st.error("❌ Database connection failed. Check credentials or internet.")
        raise

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

# --- User Management ---
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

# --- UI ---
st.set_page_config(page_title="Auth + Reels App", page_icon="🎥")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Register", "Login", "Dashboard"])
if st.sidebar.button("Init Users Table"):
    create_users_table()
    st.sidebar.success("Users table ready!")

# --- Register ---
if menu == "Register":
    st.header("📝 Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if name and email and password:
            ok, msg = register_user(name, email, password)
            if ok :
                st.success(msg) 
            else :
                st.error(msg)

        else:
            st.warning("Fill in all fields.")

# --- Login ---
elif menu == "Login":
    st.header("🔑 Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if login_user(email, password):
            st.session_state['user'] = email
            st.success("✅ Logged in")
        else:
            st.error("❌ Invalid credentials.")

# --- Dashboard ---
elif menu == "Dashboard":
    user = st.session_state.get("user")
    if not user:
        st.warning("Login first.")
    else:
        st.success(f"Welcome, {user}!")
        if st.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()

        st.markdown("## 🎞️ AI Reels Extractor")
        video_file = st.file_uploader("📹 Upload Video/Audio", type=["mp4", "mov", "avi", "mkv", "mp3", "wav"])
        if video_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                tmp.flush()
                video_path = tmp.name

        if st.button("📝 Transcribe & Analyze") and video_file:
            try:
                st.info("🔊 Transcribing with Whisper (tiny model for speed)...")
                whisper_model = whisper.load_model("tiny")  # Faster
                result = whisper_model.transcribe(video_path, verbose=False)
                segments = result["segments"]

                transcript = "\n".join(
                    f"{seg['start']:.2f} --> {seg['end']:.2f}: {seg['text'].strip()}"
                    for seg in segments
                )
                st.text_area("Transcript", transcript, height=300)

                st.info("🧠 Finding best moments with Gemini...")
                prompt = f"""
You are given a transcript with timestamps. Pick the top 3 most engaging segments, each ≤ 30s.
Keep original sentences and timestamps. Format strictly as:
[MM:SS] - [MM:SS]:
   line1
   line2 (optional)

Transcript:
{transcript}
"""
                gemini_response = gemini_model.generate_content(prompt)
                raw = gemini_response.text

                def normalize(text):
                    out = []
                    for block in text.strip().split("\n\n"):
                        lines = block.split("\n")
                        m = re.match(r"\[(\d+):(\d+\.\d+)\] - \[(\d+):(\d+\.\d+)\]:", lines[0])
                        if not m:
                            continue
                        start = int(m.group(1))*60 + float(m.group(2))
                        end = int(m.group(3))*60 + float(m.group(4))
                        if end - start <= 30:
                            out.append(block)
                    return "\n\n".join(out)

                st.session_state["segments"] = normalize(raw)
                st.code(st.session_state["segments"])
            except Exception as e:
                st.error(f"Processing error: {e}")

        if st.button("✂️ Cut Reels") and "segments" in st.session_state:
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    clips_dir = os.path.join(tmpdir, "clips")
                    os.makedirs(clips_dir, exist_ok=True)
                    final_dir = "saved_reels"
                    os.makedirs(final_dir, exist_ok=True)

                    for i, block in enumerate(st.session_state["segments"].split("\n\n")):
                        m = re.match(r"\[(\d+):(\d+\.\d+)\] - \[(\d+):(\d+\.\d+)\]:", block)
                        if not m:
                            continue
                        start = int(m.group(1))*60 + float(m.group(2))
                        end = int(m.group(3))*60 + float(m.group(4))
                        if end - start > 30:
                            continue

                        start_str = f"{int(start//3600):02}:{int((start%3600)//60):02}:{start%60:05.2f}"
                        end_str = f"{int(end//3600):02}:{int((end%3600)//60):02}:{end%60:05.2f}"

                        out_file = os.path.join(final_dir, f"reel_{i+1}.mp4")
                        cmd = [
                            "ffmpeg", "-y", "-i", video_path,
                            "-ss", start_str, "-to", end_str,
                            "-vf", "scale=720:1280,setsar=1",
                            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                            "-c:a", "aac", "-b:a", "128k",
                            out_file
                        ]
                        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if os.path.exists(out_file):
                            st.video(out_file)
                            with open(out_file, "rb") as f:
                                st.download_button(f"⬇️ Download Reel {i+1}", f, file_name=f"reel_{i+1}.mp4")
            except Exception as e:
                st.error(f"FFmpeg error: {e}")
