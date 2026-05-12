---
name: hermes-fund-manager
description: Provide Hermes personal assistant workflows for China fund management, A-share market summaries, fund holding reports, fund-news daily briefings, risk-aware portfolio adjustment suggestions, and local portfolio persistence from screenshots. Use when the user asks for A-share sector movement summaries, fund portfolio tracking, fund daily reports, investment-sector explanations, holding updates, or screenshot-based fund position extraction.
---

# Hermes Fund Manager

## Core Rules

- Treat this skill as an analysis and reporting workflow, not a trading system.
- Never output certain buy/sell commands, return promises, or personalized suitability claims.
- Use data-source priority strictly:
  1. Use Tiantian Fund skills for fund details, NAV, holdings, fund search, and index information.
  2. Use Eastmoney sector quote endpoints for A-share sector Top 5 gainers/losers because Tiantian Fund does not expose a full sector ranking skill.
  3. Use web search only as fallback for unavailable structured data or for news-cause verification.
- Explicitly disclose fallback use at the end of the report.
- Keep private portfolio data local under `C:\Users\admin\.codex\hermes\fund-manager\`; do not publish it to GitHub.

## Workflow Selection

Use the requested intent to choose one workflow:

- **A-share trading report**: market overview, major indexes, sector Top 5 gainers/losers, cause analysis, and risk-aware adjustment suggestions.
- **Personal holding report**: read local portfolio data, map holdings to funds/sectors/indexes, report same-day movement and reasons, then provide adjustment suggestions.
- **Fund news daily**: summarize today or a requested date's fund-industry news directly in chat; do not generate documents.
- **Portfolio update**: extract positions from user screenshots or structured text, normalize data, show a diff, and write only after user confirmation.

Read `references/reporting.md` before composing reports. Read `references/advice_policy.md` before giving adjustment suggestions. Read `references/ttfund.md` before calling Tiantian Fund skills.

## Portfolio Persistence

Use `scripts/portfolio_store.py` for local storage:

```powershell
python scripts/portfolio_store.py init
python scripts/portfolio_store.py show
python scripts/portfolio_store.py validate
python scripts/portfolio_store.py merge-snapshot snapshot.json
```

Default files:

- Portfolio: `C:\Users\admin\.codex\hermes\fund-manager\portfolio.json`
- Events: `C:\Users\admin\.codex\hermes\fund-manager\portfolio_events.jsonl`

Before updating holdings from a screenshot:

1. Extract fund name, code, amount, percentage, platform, and visible raw text.
2. Use Tiantian Fund search to resolve missing or ambiguous fund codes.
3. Produce a JSON snapshot matching `references/portfolio_schema.json`.
4. Run `merge-snapshot` only after the user confirms the proposed changes.

## Output Contract

Every report should include:

- Data timestamp and trading-day status.
- Market overview.
- Sector gainers/losers or holding-related movement.
- Cause analysis with source labels.
- Adjustment suggestions with evidence and risk level.
- Data-source disclosure and fallback disclosure.
- Brief risk notice: informational only, not investment advice.

Keep the response concise enough for scheduled-agent delivery. Prefer tables for Top 5 lists and holdings. Do not include raw JSON unless the user asks.
