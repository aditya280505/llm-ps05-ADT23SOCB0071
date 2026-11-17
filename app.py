import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
import time

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="Social Media Caption Generator",
    page_icon="📱",
    layout="centered"
)

# --------------------------------------------------
# 2. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f8f9fc;
}

.title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: #6C63FF;
}

.subtitle {
    text-align: center;
    font-size: 16px;
    color: #777777;
    margin-bottom: 25px;
}

.caption-box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e5e5;
    margin-bottom: 15px;
}

.stButton button {
    width: 100%;
    border-radius: 8px;
    height: 45px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------

st.markdown(
    '<div class="title">📱 Social Media Caption Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Generate creative captions and hashtags using AI</div>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# 4. PLATFORM CONFIGURATION
# --------------------------------------------------

platform_details = {

    "Instagram": {
        "tone": "Creative, catchy, engaging and friendly. Use suitable emojis.",
        "limit": "Maximum 2200 characters per caption."
    },

    "LinkedIn": {
        "tone": "Professional, informative, meaningful and conversational.",
        "limit": "Maximum 3000 characters per caption."
    },

    "X (Twitter)": {
        "tone": "Short, interesting, conversational and impactful.",
        "limit": "Maximum 280 characters per caption."
    }
}

# --------------------------------------------------
# 5. USER INPUT
# --------------------------------------------------

st.subheader("✍️ Create Your Caption")

description = st.text_area(
    "Describe your post",
    placeholder="Example: Launching my new AI-powered project that helps students learn programming...",
    height=130
)

platform = st.selectbox(
    "Choose Social Media Platform",
    ["Instagram", "LinkedIn", "X (Twitter)"]
)

st.info(
    f"**Selected Platform:** {platform}\n\n"
    f"**Writing Style:** {platform_details[platform]['tone']}"
)

# --------------------------------------------------
# 6. PROMPT ENGINEERING
# --------------------------------------------------

def create_prompt(description, platform):

    details = platform_details[platform]

    prompt = f"""
You are an expert social media content writer.

Your task is to generate exactly THREE unique social media
captions based on the user's description.

USER DESCRIPTION:
{description}

SELECTED PLATFORM:
{platform}

PLATFORM WRITING STYLE:
{details['tone']}

CAPTION LENGTH:
{details['limit']}

INSTRUCTIONS:

1. Generate exactly 3 different captions.
2. Make each caption engaging and relevant.
3. Follow the selected platform's writing style.
4. Do not repeat the same ideas.
5. Generate 4-6 relevant hashtags for each caption.
6. Keep hashtags relevant to the description.
7. Do not use unnecessary hashtags.
8. Follow the specified character limit for each caption.
9. Keep the output easy to read.

OUTPUT FORMAT:

CAPTION 1:
[Generated caption]

HASHTAGS:
[Relevant hashtags]

CAPTION 2:
[Generated caption]

HASHTAGS:
[Relevant hashtags]

CAPTION 3:
[Generated caption]

HASHTAGS:
[Relevant hashtags]

Return only the three captions and their hashtags.
"""

    return prompt

# --------------------------------------------------
# 7. GEMINI API INTEGRATION
# --------------------------------------------------

def generate_captions(description, platform):

    if not API_KEY:
        raise ValueError("Gemini API key not found.")

    client = genai.Client(api_key=API_KEY)

    prompt = create_prompt(description, platform)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            if not response.text:
                raise ValueError("Empty response from Gemini.")

            return response.text

        except Exception as e:

            error_message = str(e)

            if "503" in error_message or "UNAVAILABLE" in error_message:

                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue

            raise e

    raise Exception("Gemini service is temporarily unavailable.")
# --------------------------------------------------
# 8. GENERATE BUTTON
# --------------------------------------------------

if st.button("✨ Generate Captions", type="primary"):

    if not description.strip():

        st.warning("Please enter a description first.")

    else:

        try:

            with st.spinner("Generating creative captions using Gemini AI..."):

                result = generate_captions(
                    description,
                    platform
                )

            st.session_state["captions"] = result
            st.session_state["platform"] = platform

            st.success("Your captions have been generated successfully!")

        except Exception as e:

            st.error(f"Something went wrong: {str(e)}")

# --------------------------------------------------
# 9. DISPLAY GENERATED RESULTS
# --------------------------------------------------

if "captions" in st.session_state:

    st.divider()

    st.subheader(
        f"🎯 Generated Captions for {st.session_state['platform']}"
    )

    st.markdown(st.session_state["captions"])

    st.divider()

    st.download_button(
        label="📥 Download Captions",
        data=st.session_state["captions"],
        file_name="social_media_captions.txt",
        mime="text/plain"
    )

# --------------------------------------------------
# 10. FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    "<center>Built with ❤️ using Python, Streamlit & Google Gemini AI</center>",
    unsafe_allow_html=True
)