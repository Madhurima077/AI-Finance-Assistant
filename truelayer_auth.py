import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TRUELAYER_CLIENT_ID")
CLIENT_SECRET = os.getenv("TRUELAYER_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TRUELAYER_REDIRECT_URI")

AUTH_URL = "https://auth.truelayer-sandbox.com"
API_URL = "https://api.truelayer-sandbox.com"

def get_auth_url():
    """Generate TrueLayer login URL."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "accounts transactions offline_access",
        "providers": "mock"
    }
    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{AUTH_URL}/?{param_string}"

def exchange_code_for_token(auth_code):
    """Exchange auth code for access token."""
    response = requests.post(f"{AUTH_URL}/connect/token", data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Token exchange failed: {response.text}")

def fetch_transactions(access_token):
    """Fetch transactions from TrueLayer."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get accounts
    accounts = requests.get(
        f"{API_URL}/data/v1/accounts",
        headers=headers
    ).json()
    account_id = accounts["results"][0]["account_id"]

    # Get transactions
    txns = requests.get(
        f"{API_URL}/data/v1/accounts/{account_id}/transactions",
        headers=headers
    ).json()

    return txns["results"]

def parse_truelayer_transactions(raw_transactions):
    """Convert TrueLayer format to our standard format."""
    import pandas as pd
    
    rows = []
    for t in raw_transactions:
        rows.append({
            "date": t["timestamp"][:10],
            "merchant": t.get("merchant_name") or t.get("description", "Unknown"),
            "category": t.get("transaction_category", "Uncategorised"),
            "amount": abs(t["amount"])
        })
    
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df