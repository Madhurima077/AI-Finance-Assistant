import streamlit as st
import os
import pandas as pd
from data_processor import load_transactions, detect_anomalies
from ai_assistant import chat
from bank_parser import detect_and_parse
from truelayer_auth import get_auth_url, exchange_code_for_token, fetch_transactions, parse_truelayer_transactions

# ---- Page config ----
st.set_page_config(page_title="Finance AI Assistant", page_icon="💰", layout="centered")

# ---- Header ----
st.title("💰 Personal Finance Assistant")
st.caption("Your AI-powered spending analyst")

# ---- Check for TrueLayer callback ----
query_params = st.query_params
auth_code = query_params.get("code", None)

if auth_code and "truelayer_df" not in st.session_state:
    with st.spinner("🔗 Connecting to your bank..."):
        try:
            token = exchange_code_for_token(auth_code)
            raw = fetch_transactions(token)
            st.session_state.truelayer_df = parse_truelayer_transactions(raw)
            st.session_state.messages = []
            st.session_state.history = []
            st.query_params.clear()
            st.success("✅ Bank connected successfully!")
        except Exception as e:
            st.error(f"❌ Bank connection failed: {e}")

# ---- Data source selection ----
st.markdown("### Step 1 — Connect your data")
data_option = st.radio(
    "How would you like to load your transactions?",
    ["🏦 Connect my bank account", "📂 Upload my bank statement", "📊 Use sample data"],
    horizontal=True
)

df = None

if data_option == "🏦 Connect my bank account":
    if "truelayer_df" in st.session_state:
        df = st.session_state.truelayer_df
        st.success(f"✅ Bank connected — {len(df)} transactions loaded!")
        if st.button("🔄 Disconnect and reconnect"):
            del st.session_state.truelayer_df
            st.rerun()
    else:
        st.markdown("Connect your bank account securely via **Open Banking** 🔒")
        st.caption("Uses OAuth 2.0 — we never see your login credentials")
        
        auth_url = get_auth_url()
        st.link_button("🏦 Connect Bank Account", auth_url)
        
        st.info("""
        **How it works:**
        1. Click the button above
        2. Log in with test credentials: **john / doe**
        3. Click Allow on the consent screen
        4. You'll be redirected back automatically
        """)

elif data_option == "📂 Upload my bank statement":
    st.markdown("Upload your bank statement CSV — works with **any bank worldwide** 🌍")
    st.caption("Barclays, Lloyds, HSBC, NatWest, Monzo, Revolut, Chase, and more")

    uploaded_file = st.file_uploader("Choose your bank statement", type="csv")

    if uploaded_file:
        with st.spinner("🤖 Reading your bank statement..."):
            try:
                df = detect_and_parse(uploaded_file)
                st.success(f"✅ Loaded {len(df)} transactions!")
            except Exception as e:
                st.error(f"❌ Could not parse file: {e}")
                df = None
    else:
        st.info("👆 Upload any bank statement CSV to get started.")

else:
    df = load_transactions()
    st.success(f"✅ Loaded {len(df)} sample transactions.")

# ---- Only show app if data loaded ----
if df is not None:

    st.markdown("---")
    st.markdown("### Step 2 — Your spending overview")

    # ---- Spending overview cards ----
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"£{df['amount'].sum():,.2f}")
    col2.metric("Transactions", len(df))
    col3.metric("Avg Transaction", f"£{df['amount'].mean():.2f}")

    # ---- Anomaly alert ----
    anomalies = detect_anomalies(df)
    if anomalies:
        st.warning(f"⚠️ {len(anomalies)} unusual transaction(s) detected. Ask me about them!")

    # ---- Spending by category chart ----
    with st.expander("📊 View spending breakdown"):
        cat_spend = df.groupby("category")["amount"].sum().sort_values(ascending=True)
        st.bar_chart(cat_spend)

    st.markdown("### Step 3 — Ask your AI assistant")

    # ---- Suggested questions ----
    st.markdown("**Try asking:**")
    suggested = [
        "What did I spend the most on?",
        "Were there any unusual transactions?",
        "How can I save money?",
        "How much did I spend on food?"
    ]
    cols = st.columns(2)
    for i, q in enumerate(suggested):
        if cols[i % 2].button(q, key=f"btn_{i}"):
            st.session_state.user_input = q

    # ---- Chat interface ----
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input box
    user_input = st.chat_input("Ask about your finances...")
    if not user_input and "user_input" in st.session_state:
        user_input = st.session_state.pop("user_input")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, st.session_state.history = chat(
                    user_input, st.session_state.history, df
                )
            st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})