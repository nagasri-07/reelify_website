import streamlit as st
import os
import tempfile
import subprocess
import datetime

st.set_page_config(page_title="Video Reel Cutter", layout="centered")
st.title("🎬 Smart Video Reel Cutter (Max 30 sec)")

# Upload video
video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

# Paste GPT timestamps
timestamps_input = st.text_area("Paste GPT-generated timestamps here", placeholder="e.g.\n00:01:20 - 00:01:50: Speaker gives a powerful quote on mental health.")

if st.button("✂️ Cut Video into Reels") and video_file and timestamps_input:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, video_file.name)
        output_dir = os.path.join(tmpdir, "reels")
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(video_file.read())

        st.success("Video uploaded and timestamps received!")

        # Parse timestamps
        reels = []
        for i, line in enumerate(timestamps_input.strip().split("\n")):
            try:
                time_part = line.split(":", 1)[0].strip()
                start_time, end_time = [t.strip() for t in time_part.split("-")]
                summary = line.split(":", 1)[1].strip()

                output_filename = f"reel_{i+1}.mp4"
                output_path = os.path.join(output_dir, output_filename)

                cmd = [
                    "ffmpeg", "-i", input_path,
                    "-ss", start_time,
                    "-to", end_time,
                    "-vf", "scale=720:1280,setsar=1",  # Force vertical output
                    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k",
                    output_path
                ]

                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                reels.append((output_filename, output_path, summary))
            except Exception as e:
                st.error(f"Error in line {i+1}: {line}\n{e}")

        # Show results
        if reels:
            st.success(f"Generated {len(reels)} reels:")
            for name, path, desc in reels:
                st.video(path)
                st.caption(desc)
        else:
            st.warning("No valid reels created.")

elif st.button("✂️ Cut Video into Reels"):
    st.error("Please upload a video and paste valid timestamps.")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit & FFmpeg")
