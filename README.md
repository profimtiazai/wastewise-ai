# ♻️ WasteWise AI — Gemini Edition

An AI-powered visual waste-classification assistant built with Streamlit and the Google Gemini API.

## Features

- Upload JPG, JPEG, PNG, WEBP, HEIC or HEIF images
- Gemini multimodal image analysis
- Exactly one of 9 waste categories
- Item identification
- Description
- Practical disposal guidance
- Environmental tip
- 0–1 confidence score
- Structured JSON output
- Ambiguous-image warning
- Streamlit Community Cloud ready

## 1. Run locally

### Create virtual environment

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Install packages

```bash
pip install -r requirements.txt
```

### Set Gemini API key

macOS/Linux:
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Start

```bash
streamlit run app.py
```

Open the local URL displayed by Streamlit, normally:
http://localhost:8501

## 2. Deploy through GitHub + Streamlit Community Cloud

1. Create a GitHub repository, for example `wastewise-ai`.
2. Upload:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `WASTEWise_PROMPT.md`
   - `.gitignore`
3. Go to Streamlit Community Cloud.
4. Create/select your app.
5. Choose your GitHub repository and `app.py`.
6. Open the app's Settings → Secrets.
7. Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

8. Save the secret and reboot/redeploy the app.

IMPORTANT:
- Never put your Gemini API key in GitHub.
- Never put the key directly into `app.py`.
- Never commit `.streamlit/secrets.toml`.

## 3. Suggested GitHub structure

```text
wastewise-ai/
├── app.py
├── requirements.txt
├── README.md
├── WASTEWise_PROMPT.md
└── .gitignore
```

## 4. AI model

The application defaults to `gemini-3.8-flash`. The model can be changed from the Streamlit sidebar if your Google AI Studio/API project provides another compatible vision model.

Gemini supports multimodal image understanding and structured JSON output.
