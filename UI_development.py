import streamlit as st
import google.generativeai as genai
import os
import tempfile
import subprocess

# --- CONFIGURE GEMINI ---
API_KEY = "YOUR_API_KEY"  # 🔁 Replace with your Gemini API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- PAGE SETUP ---
st.set_page_config(page_title="🎬 AI Reels Extractor", layout="centered")
st.title("🎞️ AI-Powered Reels Extractor")
st.markdown("Upload a transcript & video. Let AI find reel-worthy segments and generate clips ≤ 30s!")

# --- INPUT SECTION ---
col1, col2 = st.columns(2)
with col1:
    transcript = st.text_area("📄 Paste Transcript (with timestamps)", height=300,
        placeholder="e.g.\n00:01:20 --> The speaker gives a powerful quote...\n00:02:10 --> Another great moment...")

with col2:
    video_file = st.file_uploader("📹 Upload Video", type=["mp4", "mov", "avi"])

# --- GEMINI ANALYSIS ---
if st.button("🧠 Analyze Transcript"):
    if transcript.strip():
        with st.spinner("Gemini is selecting reel-worthy moments..."):
            prompt = f"""
You are analyzing a video transcript with timestamps. Your task is to:

1. Identify the **top 3–5 most engaging or insightful segments**.
2. Use the **exact sentences** from the transcript (do not paraphrase).
3. You can group consecutive lines if their total duration is **30 seconds or less**.
4. If possible, try to select emotionally impactful, motivational, or key takeaway moments.

Output format:
1. [start_time] - [end_time]:
   [exact line 1]
   [exact line 2] (if grouped)

Transcript:
{transcript}
"""
            try:
                response = model.generate_content(prompt)
                refined_timestamps = response.text
                st.subheader("📌 Gemini-Selected Timestamps")
                st.code(refined_timestamps, language="text")
                st.session_state["timestamps"] = refined_timestamps  # save for reuse
            except Exception as e:
                st.error(f"❌ Gemini error: {e}")
    else:
        st.warning("Please paste a transcript.")

# --- VIDEO CUTTING ---
if st.button("✂️ Cut Video into Reels"):
    if video_file and "timestamps" in st.session_state:
        timestamps_input = st.session_state["timestamps"]

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, video_file.name)
            output_dir = os.path.join(tmpdir, "reels")
            os.makedirs(output_dir, exist_ok=True)

            # Save uploaded video
            with open(input_path, "wb") as f:
                f.write(video_file.read())

            st.success("Video uploaded and timestamps received!")

            # Parse and cut reels
            reels = []
            for i, block in enumerate(timestamps_input.strip().split("\n\n")):
                try:
                    lines = block.strip().split("\n")
                    if not lines or "-" not in lines[0]:
                        continue

                    time_line = lines[0]
                    start_time, end_time = [x.strip(" []") for x in time_line.split("-")]
                    summary = "\n".join(lines[1:]).strip()

                    output_filename = f"reel_{i+1}.mp4"
                    output_path = os.path.join(output_dir, output_filename)

                    # FFmpeg command to cut and resize
                    cmd = [
                        "ffmpeg", "-i", input_path,
                        "-ss", start_time,
                        "-to", end_time,
                        "-vf", "scale=720:1280,setsar=1",
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k",
                        output_path
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    reels.append((output_filename, output_path, summary))

                except Exception as e:
                    st.error(f"Error in block {i+1}: {block}\n\n{e}")

            # Show results
            if reels:
                st.success(f"🎉 Generated {len(reels)} reels!")
                for name, path, desc in reels:
                    st.video(path)
                    with open(path, "rb") as vid:
                        st.download_button("⬇️ Download", vid, file_name=name)
                    st.caption(desc)
            else:
                st.warning("❌ No valid reels generated.")
    else:
        st.error("Upload a video and generate timestamps first.")

# --- FOOTER ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Google Gemini, and FFmpeg.")
