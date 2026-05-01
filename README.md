
# 💰 Personal Finance AI Assistant

A conversational AI assistant that analyses personal spending data and 
answers natural language questions using Claude's API.

## What it does
- Loads transaction history from CSV
- Detects anomalous transactions using statistical analysis
- Uses Claude AI to answer spending questions in plain English
- Suggests savings based on actual spending patterns

## Tech stack
Python · Groq (Llama 3.1) · Pandas · Streamlit · TrueLayer Open Banking API

## Product thinking
This project was built with an AI Product Manager lens. See /docs for:
- Product Requirements Document (PRD)
- User stories
- Success metrics and risk analysis

## How to run
1. pip install groq pandas streamlit requests python-dotenv
2. Sign up at console.truelayer.com and get sandbox credentials
3. Run python truelayer_setup.py to connect mock bank and fetch transactions
4. Set your API keys in .env
5. streamlit run app.py

## What I learned
- LLM context injection and prompt engineering
- Statistical anomaly detection
- Translating user needs into product requirements

Note: transactions.csv contains sample/mock data for demo purposes only. 
In production, data would be fetched live via TrueLayer Open Banking API.