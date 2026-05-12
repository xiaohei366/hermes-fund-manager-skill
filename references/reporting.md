# Reporting Templates

## A-share Trading Report

Use this structure:

1. `市场概览`: major index movement, turnover, northbound/major fund flow if available, risk tone.
2. `板块涨跌Top5`: two tables, gainers and losers. Columns: sector, change %, key catalysts, source.
3. `原因分析`: explain policy, industry news, macro, earnings, liquidity, and sentiment separately when relevant.
4. `调整建议`: use the levels from `advice_policy.md`; include evidence and do not issue deterministic trades.
5. `数据来源`: list Tiantian Fund, Eastmoney, news/search fallback if used.

## Personal Holding Report

Read the local portfolio first:

```powershell
python scripts/portfolio_store.py show
```

If no holdings exist, ask the user to update holdings with a screenshot or structured list.

For each holding:

- Resolve fund details and latest NAV with Tiantian Fund.
- Use fund holdings or declared sector tags to map the fund to sectors/indexes.
- Compare holding weight with today's sector/index movement.
- Explain causes and include a specific risk-aware suggestion level.

Suggested table columns:

| 基金 | 持仓占比 | 关联方向 | 今日表现 | 原因 | 建议等级 |

## Fund News Daily

Follow the spirit of the referenced fund-news-daily skill: prioritize reliable fund-industry sources and avoid irrelevant market noise.

Sections:

1. `今日重点`: 3-5 highest-impact fund/asset-management items.
2. `政策与监管`: fund industry, fee reform, pension, ETF, asset allocation, compliance.
3. `产品与资金`: new fund issuance, ETF flow, major fund manager actions, public-fund positioning.
4. `市场影响`: connect news to A-share sectors, broad indexes, and fund categories.
5. `对持仓的启示`: only if local holdings exist.

Do not generate Word or PDF output. Answer directly in chat.

## Cause Analysis Checklist

Prefer evidence in this order:

1. Structured quote movement.
2. Same-day authoritative news.
3. Sector-specific catalyst.
4. Macro/policy context.
5. Market sentiment or technical explanation.

Avoid single-cause explanations when several forces are plausible. State uncertainty when the cause is inferred.
