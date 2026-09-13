
import base64
import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

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

OBJECTIVE
Analyze the uploaded image carefully and identify the single most likely visible waste item.

ALLOWED CATEGORIES
Choose exactly ONE:
Plastic, Paper, Glass, Metal, Organic, E-Waste, Hazardous, Textile, Other.

VISUAL ANALYSIS RULES
1. Base the decision only on what is visibly supported by the image.
2. Do not invent, assume, or mention objects that are not visible.
3. If multiple waste objects are visible, select the single most prominent or clearly identifiable waste item.
4. Classify the item according to its primary material or waste type.
5. If the image is unclear or ambiguous, select the safest reasonable category and assign a lower confidence score.
6. Do not assume recycling facilities exist everywhere.
7. Disposal advice should acknowledge that local waste-management rules can vary.
8. For hazardous or electronic waste, prioritize safe handling and authorized collection/recycling rather than ordinary household disposal.

OUTPUT REQUIREMENTS
Return ONLY valid JSON with exactly these fields:
category, item, description, disposal, tip, confidence

FIELD RULES
- category: exactly one allowed category.
- item: short, evidence-based name of the visible waste item.
- description: concise explanation of what is visibly present.
- disposal: practical, responsible and safe disposal guidance.
- tip: exactly one useful environmental or recycling tip.
- confidence: numerical value between 0 and 1.

Never return markdown, code fences, or additional fields.
"""

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": CATEGORIES},
        "item": {"type": "string"},
        "description": {"type": "string"},
        "disposal": {"type": "string"},
        "tip": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "category", "item", "description",
        "disposal", "tip", "confidence"
    ],
    "additionalProperties": False,
}

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")

def analyze_image(uploaded_file, model):
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets "
            "or set it as an environment variable."
        )

    client = genai.Client(api_key=api_key)

    image_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type or "image/jpeg"

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    response = client.models.generate_content(
        model=model,
        contents=[SYSTEM_PROMPT, image_part],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA,
            temperature=0.1,
        ),
    )

    text = response.text.strip()
    result = json.loads(text)

    if result["category"] not in CATEGORIES:
        result["category"] = "Other"

    result["confidence"] = max(
        0.0, min(1.0, float(result["confidence"]))
    )

    return result

st.markdown(
    """
    <div style="text-align:center; padding:0.5rem 0 1rem;">
        <div style="font-size:3rem;">♻️</div>
        <h1 style="margin-bottom:0.2rem;">WasteWise AI</h1>
        <p style="font-size:1.05rem;">AI-powered visual waste classification</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Upload a clear photo of a waste item. WasteWise AI identifies the most likely "
    "visible item, assigns one waste category, and provides responsible disposal guidance."
)

with st.sidebar:
    st.header("⚙️ Settings")
    model = st.text_input(
        "Gemini model",
        value="gemini-3.8-flash",
        help="Change this only if a different vision-capable Gemini model is available to your API project.",
    )
    st.divider()
    st.caption("♻️ WasteWise AI")
    st.caption("PakAngel Cohort 11 • Mid-Term Hackathon")

uploaded = st.file_uploader(
    "📷 Upload a waste image",
    type=["jpg", "jpeg", "png", "webp", "heic", "heif"],
    help="Use a clear image with the waste item visible.",
)

if uploaded:
    image = Image.open(BytesIO(uploaded.getvalue()))
    st.image(image, caption="Uploaded image", use_container_width=True)

    if st.button("🔍 Analyze Waste", type="primary", use_container_width=True):
        with st.spinner("Gemini is analyzing the image..."):
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
                "The image is relatively ambiguous. Try a clearer photo with better "
                "lighting and the item closer to the camera."
            )

        with st.expander("View structured JSON"):
            st.json(result)

else:
    st.markdown("### How it works")
    st.markdown(
        "1. **Upload** a waste photo  \n"
        "2. **Analyze** it with Gemini Vision  \n"
        "3. **Classify** it into exactly one category  \n"
        "4. **Act** on practical disposal guidance"
    )

st.divider()
st.caption(
    "WasteWise AI provides general guidance. Local waste-management rules may differ."
)
