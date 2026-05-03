import pdfplumber
import pandas as pd
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(uploaded_file):
    """Extract all text from a PDF bank statement."""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def parse_transactions_from_text(text):
    """Use AI to extract transactions from raw PDF text."""
    
    # Limit text to avoid token limits
    text_sample = text[:4000]
    
    prompt = f"""
You are a bank statement parser. Extract ALL transactions from this bank statement text.

Bank statement text:
{text_sample}

Return ONLY a JSON array of transactions. Each transaction must have exactly these fields:
- date: in YYYY-MM-DD format
- merchant: the shop, company or description
- amount: positive number only (ignore credits/income)
- category: one of these: Food & Drink, Transport, Shopping, Bills, Entertainment, Health, Travel, Income, Other

Example format:
[
  {{"date": "2024-01-15", "merchant": "Tesco", "amount": 45.20, "category": "Food & Drink"}},
  {{"date": "2024-01-16", "merchant": "TfL Oyster", "amount": 12.50, "category": "Transport"}}
]

Rules:
- Only include debit/spending transactions
- Skip income, salary, transfers in
- If date format is unclear use your best guess
- Return ONLY the JSON array, nothing else
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Clean up response in case AI adds extra text
    if "[" in raw:
        raw = raw[raw.index("["):raw.rindex("]") + 1]
    
    transactions = json.loads(raw)
    return transactions

def detect_and_parse(uploaded_file):
    """
    Main function — accepts PDF or CSV and returns standard DataFrame.
    """
    filename = uploaded_file.name.lower()
    
    if filename.endswith(".pdf"):
        return parse_pdf(uploaded_file)
    elif filename.endswith(".csv"):
        return parse_csv(uploaded_file)
    else:
        raise ValueError("Only PDF and CSV files are supported.")

def parse_pdf(uploaded_file):
    """Parse a PDF bank statement."""
    
    # Step 1 — extract text
    text = extract_text_from_pdf(uploaded_file)
    
    if not text or len(text) < 50:
        raise ValueError("Could not extract text from PDF. Make sure it's not a scanned image.")
    
    # Step 2 — AI parses transactions
    transactions = parse_transactions_from_text(text)
    
    if not transactions:
        raise ValueError("No transactions found in the PDF.")
    
    # Step 3 — convert to DataFrame
    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()
    df = df.dropna(subset=["date", "amount"])
    df = df[df["amount"] > 0]
    
    return df

def parse_csv(uploaded_file):
    """Parse any CSV bank statement using AI column detection."""
    
    df_raw = pd.read_csv(uploaded_file)
    columns = list(df_raw.columns)
    sample = df_raw.head(3).to_string()
    
    prompt = f"""
I have a bank statement CSV with these columns: {columns}

First 3 rows:
{sample}

Map these columns to our standard format. Return ONLY a JSON object:
{{
    "date": "exact column name for date",
    "merchant": "exact column name for merchant/description/payee",
    "amount": "exact column name for amount",
    "category": "exact column name for category or null if not present",
    "amount_type": "single" if one amount column, "split" if separate debit/credit columns
}}
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0
    )
    
    mapping = json.loads(response.choices[0].message.content)
    
    df = pd.DataFrame()
    df["date"] = pd.to_datetime(df_raw[mapping["date"]], dayfirst=True, errors="coerce")
    df["merchant"] = df_raw[mapping["merchant"]].astype(str)
    df["amount"] = pd.to_numeric(
        df_raw[mapping["amount"]].astype(str).str.replace(",", "").str.replace("£", ""),
        errors="coerce"
    ).abs()
    
    if mapping["category"]:
        df["category"] = df_raw[mapping["category"]].astype(str)
    else:
        df["category"] = categorise_transactions(df["merchant"].tolist())
    
    df = df.dropna(subset=["date", "amount"])
    df = df[df["amount"] > 0]
    
    return df

def categorise_transactions(merchants):
    """Use AI to categorise merchant names."""
    
    categories = [
        "Food & Drink", "Transport", "Shopping",
        "Bills", "Entertainment", "Health",
        "Travel", "Income", "Other"
    ]
    
    prompt = f"""
Categorise each merchant into one of: {categories}

Merchants: {merchants[:50]}

Return ONLY a JSON array of category strings, one per merchant.
Example: ["Food & Drink", "Transport", "Bills"]
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )
    
    result = json.loads(response.choices[0].message.content)
    
    while len(result) < len(merchants):
        result.append("Other")
    
    return result[:len(merchants)]