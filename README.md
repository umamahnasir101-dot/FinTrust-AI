# FinTrust AI 🛡️

Your AI Guardian for Financial Trust.

FinTrust AI is an autonomous AI agent that:
1. **Explains confusing financial decisions** (loans, savings, budgeting) in simple, plain language.
2. **Detects scam/fraud messages** in real time, reasoning step-by-step through red flags.

Built for underserved users who don't have access to a real financial advisor.

## Tech Stack
- Streamlit (UI)
- Groq + Llama 3.3 (agent reasoning)
- Rule-based + RAG-style knowledge grounding for literacy & scam detection

## Setup (local)
```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Groq API key either as an environment variable `GROQ_API_KEY`, or paste it into the app's input field when prompted.

## Deploy
Deployed free on Streamlit Community Cloud.
