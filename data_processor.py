import pandas as pd

def load_transactions(filepath="transactions.csv"):
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df

def get_summary(df):
    """Generate a plain-English summary of spending data."""
    total = df["amount"].sum()
    by_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_merchants = df.groupby("merchant")["amount"].sum().nlargest(5)
    avg_transaction = df["amount"].mean()
    num_transactions = len(df)
    
    summary = f"""
    SPENDING SUMMARY (Last 3 months)
    Total spent: £{total:.2f}
    Number of transactions: {num_transactions}
    Average transaction: £{avg_transaction:.2f}
    
    Spending by category:
    {by_category.to_string()}
    
    Top 5 merchants by spend:
    {top_merchants.to_string()}
    """
    return summary

def detect_anomalies(df, threshold_multiplier=3):
    """Flag transactions that are unusually high for their category."""
    anomalies = []
    for category in df["category"].unique():
        cat_df = df[df["category"] == category]
        mean = cat_df["amount"].mean()
        std = cat_df["amount"].std()
        threshold = mean + (threshold_multiplier * std)
        flagged = cat_df[cat_df["amount"] > threshold]
        for _, row in flagged.iterrows():
            anomalies.append({
                "date": row["date"].strftime("%Y-%m-%d"),
                "merchant": row["merchant"],
                "category": row["category"],
                "amount": row["amount"],
                "category_avg": round(mean, 2)
            })
    return anomalies

# Test it
if __name__ == "__main__":
    df = load_transactions()
    print(get_summary(df))
    print("\n🚨 Anomalies detected:")
    for a in detect_anomalies(df):
        print(f"  {a['date']} | {a['merchant']} | £{a['amount']} (avg for {a['category']}: £{a['category_avg']})")