
import os
from io import BytesIO
from typing import Literal

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

st.set_page_config(
    page_title="WasteWise AI",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Structured Gemini output
# -----------------------------
WasteCategory = Literal[
    "Plastic", "Paper", "Glass", "Metal", "Organic",
    "E-Waste", "Hazardous", "Textile", "Other"
]

CATEGORIES = [
    "Plastic", "Paper", "Glass", "Metal", "Organic",
    "E-Waste", "Hazardous", "Textile", "Other"
]


class WasteResult(BaseModel):
    category: WasteCategory = Field(
        description="Exactly one allowed waste category."
    )
    item: str = Field(
        description="Short name of the single visible waste item."
    )
    description: str = Field(
        description="Concise description based only on visible evidence."
    )
    disposal: str = Field(
        description="Practical and safe disposal guidance."
    )
    tip: str = Field(
        description="Exactly one useful environmental or recycling tip."
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score from 0 to 1."
    )


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
11. Keep the description concise and useful to a general user.
12. Do not identify people or provide unrelated observations.
"""


# -----------------------------
# Helpers
# -----------------------------
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

    if getattr(response, "parsed", None) is not None:
        result = response.parsed
        if isinstance(result, WasteResult):
            return result.model_dump()

    return WasteResult.model_validate_json(response.text).model_dump()


def confidence_info(value):
    if value >= 0.90:
        return "High confidence", "🟢"
    if value >= 0.70:
        return "Good confidence", "🟡"
    return "Low confidence", "🟠"


# -----------------------------
# Custom styling
# -----------------------------
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        text-align: center;
        padding: 0.5rem 0 1.2rem 0;
    }

    .hero-icon {
        font-size: 3.6rem;
        line-height: 1;
        margin-bottom: .5rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.7rem;
        letter-spacing: -1px;
    }

    .hero p {
        margin: .55rem auto 0;
        color: #64748b;
        font-size: 1.08rem;
        max-width: 620px;
    }

    .tagline {
        text-align: center;
        font-weight: 700;
        color: #166534;
        margin: .4rem 0 1.5rem;
    }

    .result-card {
        border: 1px solid rgba(22, 101, 52, .14);
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        margin: .7rem 0;
        background: rgba(248, 250, 252, .72);
    }

    .result-card h4 {
        margin: 0 0 .45rem 0;
    }

    .category-pill {
        display: inline-block;
        padding: .35rem .75rem;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-weight: 800;
        font-size: .88rem;
        letter-spacing: .3px;
    }

    .item-name {
        font-size: 1.65rem;
        font-weight: 800;
        margin: .65rem 0 .25rem;
    }

    .section-label {
        font-weight: 800;
        font-size: 1.02rem;
        margin-bottom: .25rem;
    }

    .category-list {
        text-align: center;
        color: #475569;
        line-height: 2;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: .82rem;
        margin-top: 1.4rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(15, 23, 42, .08);
        border-radius: 14px;
        padding: .7rem .9rem;
        background: rgba(248, 250, 252, .7);
    }

    @media (max-width: 640px) {
        .hero h1 { font-size: 2.25rem; }
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-icon">♻️</div>
        <h1>WasteWise AI</h1>
        <p>
            An intelligent visual waste-classification assistant that helps you
            identify waste and make more responsible disposal decisions.
        </p>
    </div>
    <div class="tagline">Identify • Classify • Dispose Responsibly</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Session state
# -----------------------------
if "result" not in st.session_state:
    st.session_state.result = None

# -----------------------------
# Advanced settings
# -----------------------------
with st.sidebar:
    st.header("⚙️ Advanced Settings")
    model = st.text_input(
        "Gemini model",
        value="gemini-3.8-flash",
        help="Use a vision-capable Gemini model available to your API project.",
    )
    st.divider()
    st.caption("WasteWise AI")
    st.caption("PakAngel Cohort 11 • Mid-Term Hackathon")

# -----------------------------
# Image source
# -----------------------------
st.markdown("### 📸 Choose how to scan")

camera_tab, upload_tab = st.tabs(["📷 Take a Photo", "🖼️ Upload an Image"])

with camera_tab:
    st.caption("Use your device camera to capture the waste item.")
    camera_image = st.camera_input(
        "Take a clear photo of the waste item",
        key="waste_camera",
        help="Place one waste item clearly in the frame and use good lighting.",
        resolution="1080p",
    )

with upload_tab:
    st.caption("Choose a clear JPG, PNG, or WebP image from your device.")
    uploaded_image = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png", "webp"],
        key="waste_upload",
        help="A clear image with the waste item visible gives better results.",
    )

image_source = camera_image if camera_image is not None else uploaded_image

if image_source is not None:
    try:
        image = Image.open(BytesIO(image_source.getvalue()))
    except Exception:
        st.error("The selected image could not be opened. Please try another image.")
        st.stop()

    st.markdown("### 🔍 Image preview")
    st.image(image, use_container_width=True)

    st.info(
        "For the best result, keep one waste item clearly visible, use good lighting, "
        "and avoid excessive background clutter."
    )

    if st.button(
        "🔍 Analyze Waste",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("🤖 WasteWise AI is examining the image..."):
            try:
                st.session_state.result = analyze_image(image_source, model)
            except Exception as exc:
                st.session_state.result = None
                st.error(f"Analysis failed: {exc}")
                st.stop()

        st.success("Analysis complete")

    # Keep the result visible across Streamlit reruns.
    result = st.session_state.result

    if result:
        st.divider()
        st.markdown("## ♻️ Waste Assessment")

        confidence = float(result["confidence"])
        confidence_label, confidence_icon = confidence_info(confidence)

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(
                f'<div class="result-card">'
                f'<div class="section-label">Category</div>'
                f'<span class="category-pill">{result["category"].upper()}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f'<div class="result-card">'
                f'<div class="section-label">AI Confidence</div>'
                f'<div style="font-size:1.35rem;font-weight:800;">'
                f'{confidence_icon} {confidence * 100:.0f}%'
                f'</div>'
                f'<div style="color:#64748b;font-size:.9rem;">'
                f'{confidence_label}'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="result-card">
                <span class="category-pill">{result["category"]}</span>
                <div class="item-name">{result["item"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns(2)

        with left:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="section-label">🔎 What I See</div>
                    <div>{result["description"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="section-label">💡 Eco Tip</div>
                    <div>{result["tip"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="result-card">
                <div class="section-label">♻️ How to Dispose</div>
                <div>{result["disposal"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if confidence < 0.55:
            st.warning(
                "The image is relatively ambiguous. Try another photo with better "
                "lighting and the item closer to the camera."
            )

        st.caption(
            "Disposal practices vary by location. Follow your local waste-management "
            "rules, especially for hazardous materials and electronic waste."
        )

        if st.button("🔄 Analyze Another Image", use_container_width=True):
            st.session_state.result = None
            st.rerun()

else:
    st.markdown(
        """
        <div class="result-card">
            <div class="section-label">🌱 What is WasteWise AI?</div>
            <div>
                WasteWise AI uses Gemini's image understanding capabilities to examine
                a visible waste item, classify it into one of nine categories, and
                provide practical disposal guidance and an environmental tip.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### How it works")

    h1, h2, h3, h4 = st.columns(4)

    with h1:
        st.markdown("**1. 📷 Capture**")
        st.caption("Take a photo or upload an image.")

    with h2:
        st.markdown("**2. 🤖 Analyze**")
        st.caption("AI examines the visible item.")

    with h3:
        st.markdown("**3. 🏷️ Classify**")
        st.caption("One waste category is selected.")

    with h4:
        st.markdown("**4. ♻️ Act**")
        st.caption("Get disposal guidance and an eco tip.")

    st.markdown("### Supported waste categories")
    st.markdown(
        '<div class="category-list">'
        + " • ".join(CATEGORIES)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="result-card">
            <div class="section-label">📌 For better results</div>
            <div>
                Photograph one item at a time, keep it clearly visible, use good
                lighting, and avoid heavy background clutter.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

st.markdown(
    """
    <div class="footer">
        ♻️ WasteWise AI • PakAngel Cohort 11 Mid-Term Hackathon<br>
        General guidance only. Local waste-management rules may differ.
    </div>
    """,
    unsafe_allow_html=True,
)
