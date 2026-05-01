import pandas as pd
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_and_parse(uploaded_file):
    """
    Accepts any bank CSV and converts it to standard format:
    date, merchant, category, amount
    """
    # Read the raw file
    df_raw = pd.read_csv(uploaded_file)
    
    # Show AI the column names and first 3 rows
    sample = df_raw.head(3).to_string()
    columns = list(df_raw.columns)
    
    # Ask AI to map the columns
    prompt = f"""
    I have a bank statement CSV with these columns: {columns}
    
    Here are the first 3 rows:
    {sample}
    
    Map these columns to our standard format. Respond ONLY with a JSON object like this:
    {{
        "date": "exact column name for date",
        "merchant": "exact column name for merchant/description/payee",
        "amount": "exact column name for amount (use debit column if separate)",
        "category": "exact column name for category or null if not present",
        "amount_type": "single" if one amount column, "split" if separate debit/credit columns
    }}
    
    Only return the JSON, nothing else.
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0
    )
    
    mapping = json.loads(response.choices[0].message.content)
    
    # Build standard dataframe
    df = pd.DataFrame()
    df["date"] = pd.to_datetime(df_raw[mapping["date"]], dayfirst=True, errors="coerce")
    df["merchant"] = df_raw[mapping["merchant"]].astype(str)
    
    # Handle split debit/credit columns
    if mapping["amount_type"] == "split":
        debit_col = mapping["amount"]
        df["amount"] = pd.to_numeric(
            df_raw[debit_col].astype(str).str.replace(",", "").str.replace("£", ""),
            errors="coerce"
        ).abs()
    else:
        df["amount"] = pd.to_numeric(
            df_raw[mapping["amount"]].astype(str).str.replace(",", "").str.replace("£", ""),
            errors="coerce"
        ).abs()
    
    # Remove rows with no amount
    df = df.dropna(subset=["amount", "date"])
    df = df[df["amount"] > 0]
    
    # If no category column, use AI to categorise
    if mapping["category"] is None:
        df["category"] = categorise_transactions(df["merchant"].tolist())
    else:
        df["category"] = df_raw[mapping["category"]].astype(str)
    
    return df

def categorise_transactions(merchants):
    """Use AI to categorise a list of merchant names."""
    
    categories = [
        "Food & Drink", "Transport", "Shopping", 
        "Bills", "Entertainment", "Health", 
        "Travel", "Income", "Other"
    ]
    
    prompt = f"""
    Categorise each merchant into one of these categories:
    {categories}
    
    Merchants: {merchants[:50]}  
    
    Respond ONLY with a JSON array of category strings, 
    one per merchant in the same order.
    Example: ["Food & Drink", "Transport", "Bills"]
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # If more merchants than categorised, fill with Other
    while len(result) < len(merchants):
        result.append("Other")
    
    return result[:len(merchants)]