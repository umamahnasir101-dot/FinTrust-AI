import streamlit as st
from groq import Groq
import os

# ---------- CONFIG ----------
st.set_page_config(page_title="FinTrust AI", page_icon="🛡️", layout="centered")

# ---------- API KEY HANDLING ----------
# On Streamlit Cloud, set this in "Secrets" as GROQ_API_KEY = "your_key_here"
api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

if not api_key:
    st.warning("⚠️ No Groq API key found. Add it in Streamlit Cloud → Settings → Secrets as GROQ_API_KEY.")
    api_key = st.text_input("Or paste your Groq API key here for local testing:", type="password")

client = Groq(api_key=api_key) if api_key else None

# ---------- SIMPLE RAG KNOWLEDGE BASE (financial literacy facts) ----------
LITERACY_KB = """
- A loan's "interest rate" is the extra cost you pay to borrow money, usually shown as a yearly percentage (APR).
- "Compound interest" means you earn (or owe) interest on top of interest already added — it grows faster than simple interest.
- An emergency fund should ideally cover 3-6 months of essential expenses, kept in an easily accessible account.
- Before taking a loan, always check: interest rate, total repayment amount, monthly installment, and any hidden fees.
- Diversifying savings (not putting all money in one place) reduces risk.
- A "budget" simply means planning your income against your expenses so you spend less than you earn.
- Credit scores affect loan approval and interest rates — paying bills on time improves it over time.
- Investment "returns" are never guaranteed — higher promised returns usually mean higher risk.
"""

# ---------- SCAM DETECTION PATTERNS (rule-based reasoning seeds) ----------
SCAM_PATTERNS = """
Common red flags in financial scam messages:
1. Urgency language ("act now", "account will be blocked", "immediate action required")
2. Requests for OTP, PIN, CNIC, or password via SMS/call/link
3. Too-good-to-be-true offers (guaranteed high returns, "you won a prize")
4. Suspicious or shortened links (bit.ly, unfamiliar domains impersonating banks)
5. Poor grammar/spelling from a supposedly official source
6. Pressure to act secretly or not tell anyone (e.g. family, bank)
7. Requests to send money first to "unlock" a bigger amount
8. Caller/sender impersonating bank/government but using personal number or generic ID
"""

SYSTEM_PROMPT = f"""You are FinTrust AI, an autonomous financial guardian agent with two roles:

ROLE 1 - FINANCIAL LITERACY ADVISOR: When a user asks a financial question (loans, savings, budgeting, investing), explain it in simple, plain language a first-time earner could understand. Use this knowledge base as ground truth:
{LITERACY_KB}

ROLE 2 - SCAM/FRAUD DETECTOR: When a user pastes a suspicious message (SMS, WhatsApp, email) and asks you to check it, reason step-by-step through these red flags:
{SCAM_PATTERNS}

Always:
- Show your reasoning step-by-step (this is important — the user wants to see HOW you concluded something, not just the final answer)
- Decide whether the message is a question (use Role 1) or a message-to-analyze (use Role 2), or both
- Keep tone warm, clear, and non-judgmental — many users have low financial literacy and may feel embarrassed
- End scam analysis with a clear verdict: "🚩 Likely Scam", "⚠️ Suspicious - Be Careful", or "✅ Looks Safe" plus your reasoning
"""

# ---------- UI ----------
st.title("🛡️ FinTrust AI")
st.caption("Your AI Guardian for Financial Trust — get simple financial guidance, and check if a message is a scam.")

with st.sidebar:
    st.header("How to use")
    st.markdown("""
    **Ask a financial question**, e.g.:
    - "Should I take a loan with 20% interest?"
    - "How do I start saving?"

    **Or paste a suspicious message**, e.g.:
    - "Your account will be blocked, send your OTP now to..."
    """)
    st.divider()
    st.caption("Built for a hackathon 🚀 | Powered by Groq + Llama")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask a financial question, or paste a suspicious message to check...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not client:
        with st.chat_message("assistant"):
            st.error("Please provide a Groq API key first (see above).")
    else:
        with st.chat_message("assistant"):
            with st.spinner("🧠 Agent reasoning through this..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                        ],
                        temperature=0.4,
                    )
                    reply = response.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

# Quick demo buttons
st.divider()
st.caption("Try a quick demo:")
col1, col2 = st.columns(2)
with col1:
    if st.button("💡 Ask: Should I take a loan?"):
        st.session_state.messages.append({
            "role": "user",
            "content": "I'm being offered a loan with 22% interest to buy a phone. Should I take it?"
        })
        st.rerun()
with col2:
    if st.button("🚩 Check a scam message"):
        st.session_state.messages.append({
            "role": "user",
            "content": "URGENT: Your bank account will be suspended in 1 hour. Reply with your OTP code immediately to verify your account and avoid suspension."
        })
        st.rerun()
