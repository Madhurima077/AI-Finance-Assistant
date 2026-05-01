import requests
import urllib.parse
import webbrowser
import json
import csv
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread


CLIENT_ID = "sandbox-financeaiassistant-f6dcac"
CLIENT_SECRET = "f07d50f8-040b-4b23-b00e-89988b385027"
REDIRECT_URI = "http://localhost:3000/callback"

# TrueLayer sandbox URLs
AUTH_URL = "https://auth.truelayer-sandbox.com"
API_URL = "https://api.truelayer-sandbox.com"

auth_code_holder = {}

class CallbackHandler(BaseHTTPRequestHandler):
    """Catches the redirect from TrueLayer after login."""
    def do_GET(self):
        # Extract the auth code from the URL
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Success! You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress server logs

def get_access_token(auth_code):
    """Exchange auth code for access token."""
    response = requests.post(f"{AUTH_URL}/connect/token", data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    })
    return response.json()["access_token"]

def fetch_transactions(access_token):
    """Fetch transactions from TrueLayer sandbox."""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get list of accounts first
    accounts = requests.get(f"{API_URL}/data/v1/accounts", headers=headers).json()
    account_id = accounts["results"][0]["account_id"]
    
    # Get transactions for that account
    txns = requests.get(
        f"{API_URL}/data/v1/accounts/{account_id}/transactions",
        headers=headers
    ).json()
    
    return txns["results"]

def save_to_csv(transactions):
    """Save in the same format our app already uses."""
    with open("transactions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "merchant", "category", "amount"])
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "date": t["timestamp"][:10],  # Just the date part
                "merchant": t.get("merchant_name") or t.get("description", "Unknown"),
                "category": t.get("transaction_category", "Uncategorised"),
                "amount": abs(t["amount"])     # TrueLayer uses negative for debits
            })
    print(f"✅ Saved {len(transactions)} transactions to transactions.csv")

# ---- Main flow ----
if __name__ == "__main__":
    # Step 1: Build the auth URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "accounts transactions offline_access",
        "providers": "mock"   # Use TrueLayer's mock bank
    }
    auth_link = f"{AUTH_URL}/?{urllib.parse.urlencode(params)}"
    
    # Step 2: Start local server to catch the redirect
    server = HTTPServer(("localhost", 3000), CallbackHandler)
    thread = Thread(target=server.handle_request)
    thread.start()
    
    # Step 3: Open browser for login
    print("🌐 Opening browser for mock bank login...")
    print("   Use these test credentials:")
    print("   Username: john")
    print("   Password: doe")
    webbrowser.open(auth_link)
    
    # Step 4: Wait for the auth code
    thread.join()
    
    if "code" not in auth_code_holder:
        print("❌ No auth code received. Check your redirect URI.")
        exit()
    
    print("✅ Auth code received!")
    
    # Step 5: Get access token
    print("🔑 Getting access token...")
    token = get_access_token(auth_code_holder["code"])
    
    # Step 6: Fetch and save transactions
    print("📥 Fetching transactions from mock bank...")
    transactions = fetch_transactions(token)
    save_to_csv(transactions)
    
    print("\n🎉 Done! Run your app now: streamlit run app.py")