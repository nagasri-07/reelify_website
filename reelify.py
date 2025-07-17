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
[0.00s - 24.88s]:  When I was a kid, the disaster we worried about most was a nuclear war. That's why we had
[24.88s - 30.92s]:  a barrel like this down in our basement filled with cans of food and water. When the nuclear
[30.92s - 37.94s]:  attack came, we were supposed to go down stairs, hunker down and eat out of that barrel.
[37.94s - 45.72s]:  Today the greatest risk of global catastrophe doesn't look like this. Instead, it looks like
[45.72s - 54.72s]:  this. If anything kills over 10 million people in the next few decades, it's most likely
[54.72s - 64.44s]:  to be a highly infectious virus rather than a war. Not missiles, but microbes. Now, part of the
[64.44s - 70.64s]:  reason for this is that we have invested a huge amount in nuclear deterrence, but we've actually
[70.64s - 78.64s]:  invested very little in a system to stop an epidemic. We're not ready for the next epidemic.
[78.64s - 86.60s]:  Let's look at Ebola. I'm sure all of you read about it in the newspaper. Lots of tough
[86.60s - 93.12s]:  challenges. I followed it carefully through the case analysis tools we used to track polio
[93.12s - 100.56s]:  eradication. As you look at what went on, the problem wasn't that there was a system that
[100.56s - 106.96s]:  didn't work well enough. The problem was that we didn't have a system at all. In fact, there
[106.96s - 114.56s]:  were some pretty obvious key missing pieces. We didn't have a group of epidemiologists ready to go
[114.56s - 121.20s]:  who would have gone, seen what the disease was, see how far it had spread. The case reports came in
[121.20s - 127.60s]:  on paper. I was very delayed before they were put online and they were extremely inaccurate. We
[127.60s - 133.28s]:  didn't have a medical team ready to go. We didn't have a way of preparing people. Now, medicine
[133.36s - 140.24s]:  and some frontiers did a great job orchestrating volunteers. But even so, we were far slower than we
[140.24s - 145.76s]:  should have been getting the thousands of workers into these countries. In a large epidemic,
[145.76s - 155.36s]:  we require us to have hundreds of thousands of workers. There was no one there to look at treatment
[155.36s - 162.08s]:  approaches. No one to look at the diagnostics. No one to figure out what tools should be used.
[162.08s - 168.48s]:  As an example, we could have taken the blood of survivors, processed it, and put that plasma
[168.48s - 175.28s]:  back in people to protect them. But that was never tried. So there was a lot that was missing.
[175.28s - 183.84s]:  And these things are really a global failure. The WHO is funded to monitor epidemics, but not to do
[183.84s - 191.28s]:  these things I talked about. Now in the movies, it's quite different. There's a group of handsome
[191.28s - 200.08s]:  epidemiologists ready to go. They move in, they save the day, but that's just pure Hollywood.
[201.84s - 208.88s]:  The failure to prepare could allow the next epidemic to be dramatically more devastating than Ebola.
[210.48s - 218.24s]:  Let's look at the progression of Ebola over this year. About 10,000 people died,
[218.80s - 225.20s]:  and nearly all were in the three bus African countries. There's three reasons why it didn't
[225.20s - 231.28s]:  spread more. The first is there was a lot of heroic work by the health workers. They found the
[231.28s - 236.48s]:  people and they prevented more infections. The second is the nature of the virus.
[236.48s - 243.04s]:  Ebola does not spread through the air. And by the time you're contagious, most people are so sick
[243.04s - 251.20s]:  that they're bedridden. Third, it didn't get into many urban areas. And that was just luck.
[252.08s - 257.20s]:  If it got into a lot more urban areas, the case numbers would have been much larger.
[257.92s - 264.88s]:  So next time we might not be so lucky, you can have a virus where people feel well enough
[264.88s - 270.72s]:  while they're infectious that they get on a plane or they go to a market. The source of the virus
[270.72s - 276.24s]:  could be a natural epidemic like Ebola or it could be bioterism. And so there are things
[276.24s - 282.00s]:  that would literally make things a thousand times worse. In fact, let's look at a model
[282.72s - 290.72s]:  of a virus spread through the air like the Spanish flu back in 1918. So here's what would happen.
[291.28s - 297.12s]:  It would spread throughout the world very, very quickly. And you can see there's over 30 million
[297.12s - 300.16s]:  people die from that epidemic.
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
