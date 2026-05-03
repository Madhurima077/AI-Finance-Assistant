# Limitations, Scope & Future Vision
## Personal Finance AI Assistant — v1.0

> ⚠️ **Disclaimer:** This is a portfolio/demonstration project built for 
> learning purposes only. It is NOT a commercial product, NOT regulated 
> financial software, and NOT affiliated with any bank or financial institution. 
> All AI-generated insights are for informational purposes only and do not 
> constitute financial advice. The developer accepts no liability for financial 
> decisions made based on this tool.

---

## What This Project Is

This app was built as an **AI Product Manager portfolio project** to demonstrate:
- Understanding of LLM integration and prompt engineering
- Product thinking (PRD, user stories, success metrics)
- Knowledge of UK fintech landscape and Open Banking
- End-to-end technical delivery from data to deployed app

It is a working prototype — not a production-ready product.

---

## Intended Scope vs What Was Built

### What was originally planned
The full vision for this product included:

| Feature | Status | Reason Not Built |
|---------|--------|-----------------|
| Live bank account connection (Open Banking) | ❌ Not built | Requires FCA authorisation — see below |
| PDF + CSV bank statement upload | ✅ Built | Core feature |
| AI spending analysis (any bank) | ✅ Built | Core feature |
| Anomaly detection | ✅ Built | Core feature |
| Savings recommendations | ✅ Built | Core feature |
| User accounts + saved history | ❌ Not built | Small project scope |
| Multi-currency support | ❌ Not built | Small project scope |
| Mobile app | ❌ Not built | Small project scope |
| PDF scanning (scanned images) | ❌ Not built | Requires OCR — small project scope |

---

## Why Live Bank Connection Was Not Built

This is the most important limitation to understand.

**The original plan** was to allow users to connect their real Barclays, 
Lloyds, or Monzo account with one click using TrueLayer's Open Banking API 
— the same technology used by Monzo, Revolut, and major UK fintech apps.

**Why it was not implemented:**

Connecting to real UK bank accounts via Open Banking requires:

1. **FCA Authorisation** — The Financial Conduct Authority requires any 
   company accessing customer bank data to be registered as an AISP 
   (Account Information Service Provider) under PSD2 regulations.

2. **Company Registration** — TrueLayer only grants production API access 
   to registered UK companies, not individual developers.

3. **Data Protection obligations** — GDPR compliance, data encryption 
   standards, and a published privacy policy are required before handling 
   real financial data.

4. **This is a portfolio project** — built by an individual developer for 
   learning and demonstration purposes. Pursuing FCA registration for a 
   demo project is not proportionate.

**What was built instead:** A sandbox version using TrueLayer's mock bank 
(test credentials only) was prototyped and tested. The OAuth 2.0 flow, 
token exchange, and transaction fetching all work correctly in sandbox mode.

**The production path is clear:** Register company → apply for FCA AISP 
authorisation → apply for TrueLayer production access → update credentials.

---

## Known Limitations

### Limitation 1 — No Live Bank Connection
**Impact:** Medium — users must manually download and upload their bank statement.

**Workaround:** Every major UK bank offers free CSV/PDF export:
- Barclays → Online Banking → Statements → Download PDF
- Lloyds → Internet Banking → Statements → View/Download
- HSBC → Online Banking → Accounts → Export
- Monzo → App → Account → Download Statement
- Revolut → App → Profile → Statements → PDF
- Starling → App → Spaces → Download CSV

**Production path:** FCA AISP registration → TrueLayer production access

---

### Limitation 2 — Text PDFs Only (No Scanned Images)
**Impact:** Low-Medium — most online banking PDFs are text-based and work fine.

**What works:** PDFs downloaded directly from online banking portals 
(Barclays, Lloyds, Monzo, Revolut etc.) — these are text-based PDFs.

**What doesn't work:** Scanned paper statements or photographed statements 
— these are image-based PDFs that require OCR.

**Production path:** Integrate AWS Textract, Google Document AI, or 
Tesseract OCR for scanned PDF support.

---

### Limitation 3 — No Persistent Storage
**Impact:** Medium — data resets when the browser tab closes. No history, 
no account, no saved insights between sessions.

**Production path:**
- Add Firebase Auth for user accounts
- Add Firestore or PostgreSQL for encrypted storage
- GDPR compliance: right to deletion, data export, privacy policy

---

### Limitation 4 — AI Cannot Give Financial Advice
**Impact:** Low — this is intentional.

Under the Financial Services and Markets Act 2000 (FSMA), giving 
personalised financial advice without FCA authorisation is illegal in the UK.

The AI is deliberately restricted to analysis and observation only:
- ✅ "You spent £320 on food delivery last month"
- ✅ "This transaction is unusually high for this category"
- ❌ "You should invest your savings in an ISA" (regulated advice)

**Production path:** Partner with an FCA-authorised financial advisor to 
offer regulated advice features within the product.

---

### Limitation 5 — API Rate Limits
**Impact:** Low now, high at scale.

Uses Groq's free API tier. Under heavy usage, responses may slow down 
or fail temporarily.

**Production path:** Move to Groq paid tier or self-host Llama 3 on a 
GPU instance.

---

### Limitation 6 — CSV Column Detection May Fail
**Impact:** Low — works for most standard bank formats.

The AI-powered column detector handles most bank CSV formats but may 
occasionally misidentify columns on unusual formats.

**Production path:** Add bank-specific parsers for top 10 UK banks as 
fallback, with manual column mapping UI as last resort.

---

### Limitation 7 — No Multi-Currency Support
**Impact:** Low for UK users.

All amounts display in GBP. Users with foreign currency accounts will 
see incorrect totals.

**Production path:** Integrate Open Exchange Rates API for real-time 
currency conversion.

---

## Future Scope — What Would Make This Better

These are features that would significantly improve the product but were 
out of scope for this portfolio project:

### 🔮 Short-term (1–3 months)
- **Real bank connection** via TrueLayer (post-FCA registration)
- **User accounts** with saved transaction history
- **Scanned PDF support** via OCR
- **Monthly spending trends** — compare this month vs last month
- **Budget setting** — let users set limits per category and alert when exceeded

### 🔮 Medium-term (3–6 months)
- **Mobile app** — React Native or Flutter
- **Recurring payment detection** — spot subscriptions and direct debits
- **Bill splitting** — identify shared expenses
- **Export reports** — download spending summary as PDF
- **Multi-currency** — for users with international accounts
- **Scheduled summaries** — weekly email digest of spending

### 🔮 Long-term (6–12 months)
- **FCA-authorised financial advice** — partner with regulated advisor
- **Open Banking production** — live connection to all UK banks
- **Credit score insights** — understand how spending affects credit
- **Investment suggestions** — ISA, pension contributions (via FCA partner)
- **Shared household budgeting** — for couples or flatmates
- **AI that learns** — personalised model that improves with usage

---

## Summary

| Category | Status |
|----------|--------|
| Core AI analysis | ✅ Working |
| PDF + CSV upload | ✅ Working |
| Anomaly detection | ✅ Working |
| Savings suggestions | ✅ Working |
| Live bank connection | ❌ Requires FCA authorisation |
| Scanned PDF support | ❌ Requires OCR integration |
| User accounts | ❌ Out of scope for v1 |
| Financial advice | ❌ Requires FCA authorisation |
| Multi-currency | ❌ Out of scope for v1 |

---

*This document was written as part of an AI Product Manager portfolio. 
Identifying limitations, understanding regulatory constraints, and defining 
a clear production path are core AI PM competencies.*