# WasteWise AI — Gemini Fixed Edition

This version fixes the Gemini `INVALID_ARGUMENT` error caused by the previous
JSON schema serialization.

## The problem that was fixed

The previous version passed a raw JSON-schema dictionary containing:

`additionalProperties`

through the Python SDK. With the installed SDK/API combination it was serialized
as `additional_properties`, which Gemini rejected.

This version uses a Pydantic `WasteResult` model directly as `response_schema`.
This is the Google-recommended Python approach for structured output.

## Streamlit Secrets

In Streamlit Cloud → App Settings → Secrets:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Do not put the key in GitHub.

## GitHub files

Replace the files in your repository with:

```text
app.py
requirements.txt
README.md
WASTEWise_PROMPT.md
.gitignore
```

After pushing to GitHub, Streamlit Community Cloud should redeploy automatically.
If it does not, use Reboot/Redeploy from the app management controls.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
streamlit run app.py
```
