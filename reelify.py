import streamlit as st
import google.generativeai as genai

# Step 1: Configure Gemini API directly (⚠️ Hardcoded for simplicity)
API_KEY = "AIzaSyDou_lfKmdoC19dqpolzGY6EY7eUskkgUI"  # Replace with your actual Gemini API key
genai.configure(api_key=API_KEY)

# Step 2: Define the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Step 3: Streamlit App UI
st.title("🎬 Transcript to Reels - Highlight Generator")
st.write("Paste your video transcript below. We'll extract the top 3–5 moments for social media reels!")

transcript = st.text_area("📄 Transcript with Timestamps", height=300, placeholder="""

type here.....
""")

if st.button("✨ Generate Reel Segments"):
    with st.spinner("Analyzing transcript with Gemini..."):
        prompt = f"""
You are analyzing a video transcript. Identify the top 3–5 most engaging or insightful moments with their timestamps.

Output format:
1. [start_time] - [end_time]: [summary of event]

Transcript:
{transcript}
        """

        try:
            response = model.generate_content(prompt)
            st.subheader("🎯 Top Moments for Reels")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
