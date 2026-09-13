# ♻️ WasteWise AI

AI-powered visual waste classification app built with Streamlit and the OpenAI Responses API.

## Features
- Upload JPG, JPEG, PNG or WEBP images
- Identifies the single most likely visible waste item
- Uses exactly one of 9 predefined categories
- Gives description, disposal guidance, one environmental tip and confidence score
- Handles ambiguous images with lower confidence
- Works locally and on Streamlit Community Cloud

## Run locally

### 1. Create a virtual environment
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

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your API key
macOS/Linux:
```bash
export OPENAI_API_KEY="YOUR_API_KEY"
```

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
```

### 4. Run
```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, normally http://localhost:8501

## Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py` and `requirements.txt`.
2. Go to https://share.streamlit.io/
3. Sign in and connect GitHub.
4. Choose **Create app**.
5. Select your repository, branch (`main`) and `app.py`.
6. Open **Advanced settings / Secrets**.
7. Add:
```toml
OPENAI_API_KEY = "YOUR_API_KEY"
```
8. Deploy.

Never commit your API key to GitHub.
