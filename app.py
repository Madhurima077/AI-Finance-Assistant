import streamlit as st
import os
from data_processor import load_transactions, detect_anomalies
from ai_assistant import chat

# ---- Page config ----
st.set_page_config(page_title="Finance AI Assistant", page_icon="💰", layout="centered")

# ---- API Key ----
# Set your key: export ANTHROPIC_API_KEY=your-key (in terminal before running)

# ---- Load data ----
@st.cache_data
def get_data():
    return load_transactions()

df = get_data()

# ---- Header ----
st.title("💰 Personal Finance Assistant")
st.caption("Your AI-powered spending analyst")

# ---- Spending overview cards ----
col1, col2, col3 = st.columns(3)
col1.metric("Total Spent (3 months)", f"£{df['amount'].sum():,.2f}")
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
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, st.session_state.history = chat(
                user_input, st.session_state.history, df
            )
        st.write(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})