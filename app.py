
import base64
import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from openai import OpenAI

st.set_page_config(
    page_title="WasteWise AI",
    page_icon="♻️",
    layout="centered",
)

CATEGORIES = [
    "Plastic", "Paper", "Glass", "Metal", "Organic",
    "E-Waste", "Hazardous", "Textile", "Other"
]

SYSTEM_PROMPT = """
You are WasteWise AI, an intelligent visual waste-classification assistant.

Your job is to inspect ONE uploaded image and identify the single most likely visible
waste item. Do not invent, assume, or describe objects that are not visibly supported
by the image.

Allowed categories (choose exactly one):
Plastic, Paper, Glass, Metal, Organic, E-Waste, Hazardous, Textile, Other.

Important classification rules:
1. Identify the primary/single most visually evident waste item.
2. Choose exactly one category from the allowed list.
3. Base the decision only on visible evidence.
4. If multiple objects are visible, select the most prominent waste item.
5. If the item is unclear or ambiguous, choose the safest reasonable category and
   lower the confidence score.
6. Confidence must be a number from 0 to 1.
7. Disposal advice must be practical and safety-conscious. Do not recommend unsafe
   handling of hazardous or electronic waste.
8. Do not claim that an item is recyclable everywhere. Recycling rules vary by locality.
9. Return ONLY valid JSON with exactly these keys:
   category, item, description, disposal, tip, confidence
10. No markdown, no code fences, no extra keys.

Field requirements:
- category: one exact allowed category.
- item: short name of the visible item.
- description: concise explanation of what is visible.
- disposal: practical responsible disposal guidance.
- tip: one useful environmental/recycling tip.
- confidence: decimal number between 0 and 1.
"""

def get_api_key():
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")

def image_to_data_url(uploaded_file):
    raw = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/jpeg"
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{encoded}"

def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)

def validate_result(data):
    if not isinstance(data, dict):
        raise ValueError("The AI returned an invalid result.")
    required = ["category", "item", "description", "disposal", "tip", "confidence"]
    if any(k not in data for k in required):
        raise ValueError("The AI response is missing required fields.")
    if data["category"] not in CATEGORIES:
        data["category"] = "Other"
    try:
        data["confidence"] = max(0.0, min(1.0, float(data["confidence"])))
    except Exception:
        data["confidence"] = 0.25
    return data

def analyze_image(uploaded_file, model):
    client = OpenAI(api_key=get_api_key())
    image_url = image_to_data_url(uploaded_file)

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Analyze this uploaded waste image according to your instructions."
                },
                {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": "high"
                }
            ]
        }]
    )
    return validate_result(clean_json(response.output_text))

st.markdown(
    """
    <div style="text-align:center; padding: 0.5rem 0 1rem;">
        <div style="font-size:3rem;">♻️</div>
        <h1 style="margin-bottom:0.2rem;">WasteWise AI</h1>
        <p style="font-size:1.05rem;">AI-powered visual waste classification</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Upload a clear photo of a waste item. WasteWise AI identifies the most likely "
    "visible item, assigns one waste category, and provides disposal guidance."
)

with st.sidebar:
    st.header("⚙️ Settings")
    model = st.text_input("Vision model", value="gpt-5.6-luna")
    st.caption("The model name can be changed here if your API project uses a different vision model.")
    st.divider()
    st.caption("WasteWise AI • PakAngel Cohort 11 Mid-Term Hackathon")

uploaded = st.file_uploader(
    "📷 Upload a waste image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Use a clear image with the waste item visible.",
)

if uploaded:
    image = Image.open(BytesIO(uploaded.getvalue()))
    st.image(image, caption="Uploaded image", use_container_width=True)

    if st.button("🔍 Analyze Waste", type="primary", use_container_width=True):
        if not get_api_key():
            st.error(
                "OpenAI API key not found. Add OPENAI_API_KEY to Streamlit Secrets "
                "or set it as an environment variable."
            )
            st.stop()

        with st.spinner("Analyzing the image..."):
            try:
                result = analyze_image(uploaded, model)
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

        st.success("Analysis complete")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Category", result["category"])
        with col2:
            st.metric("Confidence", f'{result["confidence"]:.2f}')

        st.subheader("🗑️ Identified item")
        st.write(result["item"])

        st.subheader("📝 Description")
        st.write(result["description"])

        st.subheader("♻️ Disposal")
        st.write(result["disposal"])

        st.subheader("💡 Tip")
        st.write(result["tip"])

        if result["confidence"] < 0.55:
            st.warning(
                "The image is relatively ambiguous. Consider taking a clearer photo "
                "with the item closer to the camera and better lighting."
            )

        with st.expander("View structured result"):
            st.json(result)
else:
    st.markdown("### How it works")
    st.markdown(
        "1. **Upload** a waste photo  \n"
        "2. **Analyze** the visible item with AI vision  \n"
        "3. **Classify** it into exactly one category  \n"
        "4. **Act** on practical disposal guidance"
    )

st.divider()
st.caption("WasteWise AI provides general guidance. Local waste-management rules may differ.")
