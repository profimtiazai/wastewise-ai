# WasteWise AI v3 — Camera + Polished Interface

WasteWise AI is an intelligent visual waste-classification assistant using Gemini's
multimodal image understanding.

## What's new in v3

- 📷 Direct camera capture with Streamlit `st.camera_input`
- 🖼️ Image upload remains available
- ✨ Cleaner, more professional interface
- ♻️ Visual waste-assessment result cards
- 📊 Human-readable confidence levels
- 📝 Clear "What I See", disposal guidance, and eco tip
- 🔄 Analyze Another Image button
- 📱 More mobile-friendly layout
- 🏷️ Supported waste categories section
- ❌ Removed the unnecessary visible structured JSON output
- ⚙️ Gemini model remains available under Advanced Settings
- 🔐 Gemini API key continues to be read from Streamlit Secrets

## Streamlit Secrets

In Streamlit Cloud → App Settings → Secrets:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Do not put the API key in GitHub.

## GitHub files

Replace your existing project files with:

```text
app.py
requirements.txt
README.md
WASTEWise_PROMPT.md
.gitignore
```

Streamlit's `st.camera_input` returns an `UploadedFile`, so the captured image
can use the same analysis pipeline as an uploaded file.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
streamlit run app.py
```

## Notes

Camera access depends on the browser/device permission. On a phone, the browser
will normally ask permission to use the camera the first time the camera widget
is used.

WasteWise AI provides general guidance. Local waste-management rules may differ.
