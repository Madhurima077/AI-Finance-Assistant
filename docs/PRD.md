# Product Requirements Document (PRD)
## Personal Finance AI Assistant — v1.0

### Problem
Users lack visibility into their spending patterns and find 
manual budgeting tedious. Existing tools show charts but 
don't explain what the data means or what to do about it.

### Solution
A conversational AI assistant that interprets personal 
transaction data via Open Banking and answers natural 
language questions about spending.

### Target Users
25–40 year olds managing personal finances, comfortable 
with technology, based in the UK.

### Data Source
TrueLayer Open Banking API (sandbox) — the same 
infrastructure used by Monzo, Revolut, and major UK 
fintech apps. Users connect their bank account securely 
via OAuth 2.0. No credentials are ever stored.

### Scope v1
- ✅ Natural language Q&A on transaction history
- ✅ Automatic expense categorisation
- ✅ Anomaly detection and alerts
- ✅ Savings suggestions based on actual spend
- ✅ Secure bank connection via Open Banking (TrueLayer)
- ❌ Out of scope: Bill payments, investment advice, 
     multi-currency support

### Success Criteria
- Task completion rate > 85% in user testing
- No hallucinated financial figures in 100 test queries
- Anomaly precision > 80%
- Bank connection success rate > 90%

### Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| AI gives wrong figures | High | Ground model in real data only |
| Hallucinated advice | High | Restrict to analysis, not advice |
| User data privacy | Critical | OAuth only, no credentials stored |
| FCA regulation | High | Analysis only — no financial advice |
| Anomaly false positives | Medium | Allow users to dismiss flags |

### Launch Plan
Internal alpha → 50-u