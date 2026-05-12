---
name: hermes-fund-manager
description: 为 Hermes 个人助理提供中文优先的基金管理工作流，包括 A 股市场汇报、板块涨跌 Top5、基金持仓跟踪、基金行业日报、风险型持仓调整建议，以及从截图识别并本地持久化基金持仓。适用于用户询问 A 股板块汇报、基金持仓跟踪、基金日报、投资板块解释、持仓更新、截图识别基金仓位等场景。
---

# Hermes 基金管理

## 核心规则

- 默认使用中文回答；如果用户明确要求英文，再切换为英文。
- 将本 Skill 视为“分析与汇报工作流”，不是交易系统。
- 不输出确定性买卖指令、收益承诺或个性化适当性结论。
- 严格按数据源优先级取数：
  1. 基金详情、净值、基金持仓、基金搜索、指数信息优先使用天天基金 Skill。
  2. A 股板块涨跌 Top5 使用东方财富板块行情，因为天天基金当前没有全市场板块排行榜能力。
  3. 只有结构化数据不可用或需要新闻原因验证时，才使用网络搜索兜底。
- 如果使用了兜底数据，必须在报告结尾明确说明。
- 私人持仓数据只保存在 `C:\Users\admin\.codex\hermes\fund-manager\`，不要发布到 GitHub。

## 工作流选择

根据用户意图选择一个工作流：

- **A 股交易时段汇报**：市场概览、主要指数、板块涨跌 Top5、原因分析、风险型调整建议。
- **个人持仓汇报**：读取本地持仓，映射基金/板块/指数，汇报当天涨跌、原因和调整建议。
- **基金行业日报**：汇总今天或指定日期的基金行业新闻，直接在聊天中回答，不生成文档。
- **持仓更新**：从截图或结构化文本抽取持仓，归一化数据，先展示 diff，用户确认后再写入本地。

写报告前读取 `references/reporting.md`。给调整建议前读取 `references/advice_policy.md`。调用天天基金前读取 `references/ttfund.md`。

## 本地持仓持久化

使用 `scripts/portfolio_store.py` 管理本地持仓：

```powershell
python scripts/portfolio_store.py init
python scripts/portfolio_store.py show
python scripts/portfolio_store.py validate
python scripts/portfolio_store.py merge-snapshot snapshot.json
```

默认文件：

- 持仓：`C:\Users\admin\.codex\hermes\fund-manager\portfolio.json`
- 事件：`C:\Users\admin\.codex\hermes\fund-manager\portfolio_events.jsonl`

从截图更新持仓前：

1. 识别基金名称、基金代码、持仓金额、占比、平台和原始可见文本。
2. 用天天基金搜索补全或校验缺失/不确定的基金代码。
3. 生成符合 `references/portfolio_schema.json` 的 JSON 快照。
4. 展示新增、删除、金额变化、占比变化和板块标签变化。
5. 只有用户确认后，才运行 `merge-snapshot` 写入本地。

## 输出约定

每次汇报应包含：

- 数据时间和交易日状态。
- 市场概览。
- 板块涨跌或持仓相关方向表现。
- 带来源标签的原因分析。
- 有证据支撑的调整建议和风险等级。
- 数据来源和兜底说明。
- 简短风险提示：仅供信息参考，不构成投资建议。

中文报告建议使用以下标题：

- `市场概览`
- `板块涨跌Top5`
- `持仓影响`
- `原因分析`
- `调整建议`
- `数据来源`
- `风险提示`

定时智能体场景下保持内容精炼。Top5 和持仓明细优先使用表格。除非用户要求，不要输出原始 JSON。
