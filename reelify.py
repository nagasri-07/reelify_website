

import streamlit as st
import google.generativeai as genai

# Step 1: Configure Gemini with your API key
API_KEY = "AIzaSyDou_lfKmdoC19dqpolzGY6EY7eUskkgUI"  # 🔁 Replace with your Gemini API key
genai.configure(api_key=API_KEY)

# Step 2: Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Step 3: Streamlit App UI
st.title("🎞️ Reels Extractor - Gemini + Exact Transcript")
st.write("Upload your transcript with timestamps. This tool finds 3–5 engaging moments without paraphrasing and ensures segments are ≤ 30 seconds.")

# Transcript input box
transcript = st.text_area("📄 Transcript (with timestamps)", height=300, placeholder="""
type here....
""")

if st.button("🧠 Analyze Transcript"):
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
   ...

Transcript:
{transcript}
        """

        try:
            response = model.generate_content(prompt)
            st.subheader("🎯 Highlighted Reel Segments")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ Error from Gemini: {e}")
