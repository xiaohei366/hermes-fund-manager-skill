# Hermes Fund Manager Skill

`hermes-fund-manager` is a Codex/Hermes skill for China fund-management workflows. It helps an agent produce A-share market summaries, fund holding reports, fund-news daily briefings, and risk-aware portfolio adjustment suggestions.

The skill is designed for scheduled-agent scenarios, but it does not include scheduling. A scheduler should invoke the skill with a normal prompt.

## What It Does

- Summarizes the A-share market during trading days.
- Reports Top 5 rising and falling A-share sectors using Eastmoney sector quote data.
- Uses Tiantian Fund as the preferred source for fund details, NAV, fund holdings, fund search, and index data.
- Reads local fund-holding data and explains how the user's invested sectors moved.
- Produces fund-news daily briefings directly in chat.
- Gives risk-aware adjustment suggestions such as `保持观察`, `考虑再平衡`, `降低追涨风险`, `关注补仓窗口`, and `风险预警`.
- Updates local portfolio data from screenshots or structured extracted holdings after user confirmation.

It does not provide guaranteed returns, deterministic buy/sell commands, or personalized suitability claims.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── advice_policy.md
│   ├── portfolio_schema.json
│   ├── reporting.md
│   └── ttfund.md
├── scripts/
│   ├── __init__.py
│   └── portfolio_store.py
└── tests/
    └── test_portfolio_store.py
```

## Install

Clone or copy this repository into your Codex skills directory with the folder name `hermes-fund-manager`.

Example Windows path:

```powershell
C:\Users\admin\.codex\skills\hermes-fund-manager
```

Expected skill entrypoint:

```powershell
C:\Users\admin\.codex\skills\hermes-fund-manager\SKILL.md
```

## Data Sources

Use this priority order:

1. Tiantian Fund skills for fund details, NAV, fund holdings, fund search, and index information.
2. Eastmoney sector quote data for A-share sector Top 5 gainers/losers.
3. Web search only as fallback for unavailable structured data or cause verification.

If Tiantian Fund is unavailable and fallback data is used, the agent must explicitly disclose that in the report.

## Tiantian Fund API Key

Set `TTFUND_APIKEY` before using Tiantian Fund skills.

If the key is missing, the skill instructs the agent to stop Tiantian calls and say:

```text
当前未检测到 TTFUND_APIKEY，请先前往天天基金搜索 skills 获取 apikey，并在本机配置该环境变量后重试。
```

## Local Portfolio Storage

Private portfolio data is intentionally not stored in this repository.

Default local files:

```text
C:\Users\admin\.codex\hermes\fund-manager\portfolio.json
C:\Users\admin\.codex\hermes\fund-manager\portfolio_events.jsonl
```

Common commands:

```powershell
python scripts/portfolio_store.py init
python scripts/portfolio_store.py show
python scripts/portfolio_store.py validate
python scripts/portfolio_store.py merge-snapshot snapshot.json
```

The `merge-snapshot` command expects JSON shaped like `references/portfolio_schema.json`. When the data comes from a screenshot, the agent should first extract a candidate snapshot, show a diff to the user, and write only after confirmation.

## Example Prompts

```text
Use $hermes-fund-manager to summarize today's A-share market and explain the top rising and falling sectors.
```

```text
Use $hermes-fund-manager to read my local fund holdings and report today's movement, causes, and risk-aware adjustment suggestions.
```

```text
Use $hermes-fund-manager to produce today's fund-news daily report. Answer directly in chat and do not create a document.
```

```text
Use $hermes-fund-manager to update my fund holdings from this screenshot. Show the diff before writing local portfolio data.
```

## Validation

Run the skill validator:

```powershell
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\admin\.codex\skills\hermes-fund-manager
```

Run the portfolio tests:

```powershell
python -m unittest tests.test_portfolio_store -v
```

## Privacy

Do not commit:

- `portfolio.json`
- `portfolio_events.jsonl`
- screenshots
- API keys
- `.env` files
- cache directories

The included `.gitignore` excludes these private or generated files.
