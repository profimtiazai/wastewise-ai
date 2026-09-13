
import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal

st.set_page_config(page_title="WasteWise AI", page_icon="♻️", layout="centered")

CATEGORIES = [
    "Plastic", "Paper", "Glass", "Metal", "Organic",
    "E-Waste", "Hazardous", "Textile", "Other"
]

WasteCategory = Literal[
    "Plastic", "Paper", "Glass", "Metal", "Organic",
    "E-Waste", "Hazardous", "Textile", "Other"
]

class WasteResult(BaseModel):
    category: WasteCategory = Field(description="Exactly one allowed waste category.")
    item: str = Field(description="Short name of the single visible waste item.")
    description: str = Field(description="Concise description based only on visible evidence.")
    disposal: str = Field(description="Practical and safe disposal guidance.")
    tip: str = Field(description="Exactly one useful environmental or recycling tip.")
    confidence: float = Field(ge=0, le=1, description="Confidence score from 0 to 1.")

SYSTEM_PROMPT = """
You are WasteWise AI, an intelligent visual waste-classification assistant.

Analyze the uploaded image carefully and identify the single most likely visible waste item.

Choose exactly ONE category:
Plastic, Paper, Glass, Metal, Organic, E-Waste, Hazardous, Textile, Other.

Rules:
1. Base the decision only on visible evidence.
2. Never invent objects that are not visible.
3. If multiple waste objects are visible, select the single most prominent or clearly identifiable waste item.
4. Classify according to the item's primary material or waste type.
5. If the image is unclear or ambiguous, choose the safest reasonable category and give a lower confidence score.
6. Do not assume recycling facilities exist everywhere.
7. Disposal guidance should acknowledge that local waste-management rules vary.
8. For hazardous or electronic waste, recommend safe handling and authorized collection/recycling.
9. Return exactly one category.
10. Confidence must be between 0 and 1.
"""

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
            "Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets."
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
            response_schema=WasteResult,
            temperature=0.1,
        ),
    )

    # Pydantic validation makes the response reliable and avoids the
    # JSON-schema serialization problem in the previous version.
    if getattr(response, "parsed", None) is not None:
        result = response.parsed
        if isinstance(result, WasteResult):
            return result.model_dump()

    return WasteResult.model_validate_json(response.text).model_dump()

st.markdown(
    """
    <div style="text-align:center;padding:.5rem 0 1rem;">
        <div style="font-size:3rem;">♻️</div>
        <h1 style="margin-bottom:.2rem;">WasteWise AI</h1>
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
        help="Use a vision-capable Gemini model available to your API project.",
    )
    st.divider()
    st.caption("♻️ WasteWise AI")
    st.caption("PakAngel Cohort 11 • Mid-Term Hackathon")

uploaded = st.file_uploader(
    "📷 Upload a waste image",
    type=["jpg", "jpeg", "png", "webp"],
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
st.caption("WasteWise AI provides general guidance. Local waste-management rules may differ.")
