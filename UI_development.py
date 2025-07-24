import streamlit as st
import os
from pathlib import Path

# Mock video processing function (replace with actual logic)
def process_video(uploaded_video):
    import time
    time.sleep(3)  # simulate processing delay
    # Dummy file paths (replace with actual output file paths from processing logic)
    return ["sample_reel1.mp4", "sample_reel2.mp4"]

# Page config
st.set_page_config(page_title="Reel Generator", layout="centered")

st.title("🎬 Video to Reels Converter")

# Upload Section
uploaded_video = st.file_uploader("Upload your video", type=["mp4", "mov", "avi"])

if uploaded_video is not None:
    try:
        # Save uploaded file temporarily
        temp_video_path = Path("temp_upload") / uploaded_video.name
        os.makedirs(temp_video_path.parent, exist_ok=True)
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())
        
        # Show spinner while processing
        with st.spinner("Processing your video into reels..."):
            generated_reels = process_video(temp_video_path)

        # Success message
        st.success("✅ Reels generated successfully!")

        # Reel Preview Section
        st.subheader("🎞 Preview Reels")
        for reel_path in generated_reels:
            st.video(reel_path)
            with open(reel_path, "rb") as video_file:
                st.download_button(
                    label="Download",
                    data=video_file,
                    file_name=os.path.basename(reel_path),
                    mime="video/mp4"
                )

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        st.toast("Something went wrong!", icon="🚨")

else:
    st.info("Please upload a .mp4, .mov, or .avi file to begin.")
