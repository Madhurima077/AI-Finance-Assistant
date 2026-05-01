# User Stories
## Personal Finance AI Assistant

### Core Stories

**Story 1 — Spending Overview**
As a user who loses track of monthly spending,
I want to ask the AI what I spent the most on,
So that I can identify my biggest spending areas quickly.

**Story 2 — Anomaly Detection**
As a user who wants to spot unusual charges,
I want the AI to flag transactions that seem too high,
So that I can catch billing errors or fraud early.

**Story 3 — Savings Advice**
As a user who overspends on food delivery,
I want personalised suggestions based on my actual data,
So that I can make realistic changes to my spending habits.

**Story 4 — Bank Connection**
As a user who doesn't want to upload files manually,
I want to securely connect my bank account via Open Banking,
So that the AI analyses my real transactions automatically.

**Story 5 — Category Breakdown**
As a user who receives their salary on the 25th,
I want to see my spending broken down by category,
So that I can understand where my money goes each month.

### Acceptance Criteria
- AI must reference specific numbers from actual data
- AI must never give regulated financial advice
- Bank connection must use OAuth 2.0 (no credential storage)
- Anomaly alerts must show the normal average for context
- All responses must be in plain English, not financial jargon 