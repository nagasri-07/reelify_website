import streamlit as st
import google.generativeai as genai
import tempfile
import subprocess
import os
import whisper

# --- CONFIGURE GEMINI ---
API_KEY = "AIzaSyDuiPg8TvjH7FinQLiz599b4kId4LkbPCQ"  # 🔁 Replace with your Gemini API key
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# --- PAGE SETUP ---
st.set_page_config(page_title="🎬 AI Reels Extractor", layout="centered")
st.title("🎞️ AI-Powered Reels Extractor")
st.markdown("Upload a video. We'll transcribe it, find top 3 best moments (≤30s), and generate reels!")

# --- UPLOAD VIDEO ---
video_file = st.file_uploader("📹 Upload Video/Audio", type=["mp4", "mov", "avi", "mkv", "mp3", "wav"])
if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(video_file.read())
        tmp.flush()
        video_path = tmp.name

# --- TRANSCRIBE USING WHISPER ---
if st.button("📝 Transcribe & Analyze"):
    if video_file:
        st.info("🔊 Transcribing with Whisper...")
        whisper_model = whisper.load_model("base")
        result = whisper_model.transcribe(video_path, verbose=False)
        segments = result["segments"]

        # Format transcript with timestamps
        transcript_with_timestamps = ""
        for seg in segments:
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip()
            transcript_with_timestamps += f"{start:.2f} --> {end:.2f}: {text}\n"

        st.subheader("📄 Full Transcript with Timestamps")
        st.text_area("Transcript", transcript_with_timestamps, height=300)

        # --- GEMINI ANALYSIS ---
        st.info("🧠 Gemini is selecting reel-worthy moments...")
        gemini_prompt = f"""
You are analyzing a video transcript with timestamps. Your task is to:

1. Identify the **top 3 most engaging or insightful segments**.
2. Use the **exact sentences** from the transcript (no paraphrasing).
3. You can group consecutive lines if their **total duration is ≤ 30 seconds**.
4. Prioritize emotionally impactful, motivational, or insightful quotes.

Output format:
[start_time] - [end_time]: 
   [line 1]
   [line 2] (optional, if grouped)

Transcript:
{transcript_with_timestamps}
"""
        try:
            gemini_response = gemini_model.generate_content(gemini_prompt)
            selected_segments = gemini_response.text
            st.session_state["segments"] = selected_segments

            st.subheader("✅ Top Moments (from Gemini)")
            st.code(selected_segments, language="text")
        except Exception as e:
            st.error(f"Gemini error: {e}")
    else:
        st.warning("Please upload a video file.")

# --- CUT REELS USING FFMPEG ---
if st.button("✂️ Cut Reels"):
    if "segments" in st.session_state and video_file:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = video_path
            output_dir = os.path.join(tmpdir, "clips")
            os.makedirs(output_dir, exist_ok=True)

            reels = []
            for i, block in enumerate(st.session_state["segments"].strip().split("\n\n")):
                try:
                    lines = block.strip().split("\n")
                    if not lines or "-" not in lines[0]:
                        continue
                    time_line = lines[0]
                    start_time, end_time = [x.strip(" []s") for x in time_line.split("-")]
                    summary = "\n".join(lines[1:]).strip()

                    output_filename = f"reel_{i+1}.mp4"
                    output_path = os.path.join(output_dir, output_filename)

                    # FFmpeg cut
                    cmd = [
                        "ffmpeg", "-i", input_path,
                        "-ss", start_time, "-to", end_time,
                        "-vf", "scale=720:1280,setsar=1",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k",
                        output_path
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    reels.append((output_filename, output_path, summary))
                except Exception as e:
                    st.error(f"Block {i+1} failed: {e}")

            # Display clips
            if reels:
                st.success(f"🎉 {len(reels)} reels generated!")
                for name, path, desc in reels:
                    st.video(path)
                    with open(path, "rb") as f:
                        st.download_button(f"⬇️ Download {name}", f, file_name=name)
                    st.caption(desc)
            else:
                st.warning("No valid reels generated.")
    else:
        st.warning("Please transcribe and generate top segments first.")

# --- FOOTER ---
st.markdown("---")
st.caption("Built with ❤️ using Whisper, Gemini, and FFmpeg.")
