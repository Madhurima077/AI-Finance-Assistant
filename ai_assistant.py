from dotenv import load_dotenv
import os
from groq import Groq
from data_processor import load_transactions, get_summary, detect_anomalies

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_system_prompt(df):
    summary = get_summary(df)
    anomalies = detect_anomalies(df)

    anomaly_text = ""
    if anomalies:
        anomaly_text = "\n\nFLAGGED TRANSACTIONS (unusual spend):\n"
        for a in anomalies:
            anomaly_text += f"- {a['date']}: £{a['amount']} at {a['merchant']} (normal avg: £{a['category_avg']})\n"

    return f"""You are a helpful personal finance assistant.
You have access to the user's transaction data for the last 3 months.

{summary}
{anomaly_text}

Your job is to:
1. Answer questions about their spending clearly and helpfully
2. Point out flagged unusual transactions when relevant
3. Suggest practical ways to save money based on actual spending
4. Be encouraging, not judgmental

Always refer to specific numbers from their data. Keep responses concise and actionable."""

def chat(user_message, conversation_history, df):
    system_prompt = build_system_prompt(df)

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            *conversation_history
        ],
        max_tokens=500,
        temperature=0.7
    )

    assistant_message = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message, conversation_history

if __name__ == "__main__":
    df = load_transactions()
    history = []

    questions = [
        "What did I spend the most on last 3 months?",
        "Were there any unusual transactions?",
        "How can I save money based on my spending?"
    ]

    for q in questions:
        print(f"\n👤 You: {q}")
        response, history = chat(q, history, df)
        print(f"🤖 Assistant: {response}")