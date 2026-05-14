# Hermes 基金管理 Skill

`hermes-fund-manager` 是一个面向 Hermes / Codex 个人助理的基金管理 Skill，主要服务于中文对话和定时智能体场景。它负责汇报 A 股市场、基金持仓、基金行业新闻，并给出偏风控视角的持仓调整建议。

这个 Skill **不包含定时调度**。如果要定时执行，请由 Hermes 或其他调度器按固定时间触发普通对话提示词。

## 核心能力

- 汇报交易日 A 股整体情况。
- 使用东方财富板块行情汇报当日涨幅 Top5 和跌幅 Top5 板块。
- 优先使用天天基金 Skill 查询基金详情、净值、基金持仓、基金搜索和指数信息。
- 读取本地持仓数据，分析你投资方向当天的涨跌和原因。
- 生成基金行业日报，直接在聊天中回答，不生成 Word/PDF 文档。
- 输出风控型调整建议：`保持观察`、`考虑再平衡`、`降低追涨风险`、`关注补仓窗口`、`风险预警`。
- 根据截图或结构化文本更新本地持仓数据；更新前必须展示差异并等待确认。

它不会输出“必须买入/立即卖出/保证收益”等确定性投资指令，也不会承诺收益。

## 目录结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── advice_policy.md
│   ├── data_validation.md
│   ├── portfolio_schema.json
│   ├── reporting.md
│   └── ttfund.md
├── scripts/
│   ├── __init__.py
│   ├── portfolio_store.py
│   └── render_report.py
└── tests/
    ├── test_portfolio_store.py
    └── test_render_report.py
```

## 安装方式

把仓库克隆或复制到 Codex skills 目录，并确保目录名是 `hermes-fund-manager`。

Windows 示例：

```powershell
C:\Users\admin\.codex\skills\hermes-fund-manager
```

Skill 入口应位于：

```powershell
C:\Users\admin\.codex\skills\hermes-fund-manager\SKILL.md
```

## 数据源策略

按以下优先级取数：

1. **天天基金 Skill**：基金详情、净值、基金持仓、基金搜索、指数信息。
2. **东方财富板块行情**：A 股板块涨跌 Top5。天天基金当前没有“全市场板块涨跌排行榜”能力。
3. **网络搜索兜底**：当结构化数据不可用，或需要补充新闻原因时使用。

如果使用了兜底数据，报告结尾必须显式说明。

报告中的行情、板块、新闻原因和调整建议会标注 `双源一致 / 多源确认 / 单源待验证 / 数据分歧`。板块涨跌以东方财富为主，但需要至少尝试一个其他来源做交叉验证。

## 天天基金 API Key

使用天天基金 Skill 前需要配置环境变量 `TTFUND_APIKEY`。

如果没有配置，智能体应停止天天基金查询，并提示：

```text
当前未检测到 TTFUND_APIKEY，请先前往天天基金搜索 skills 获取 apikey，并在本机配置该环境变量后重试。
```

## 本地持仓数据

真实持仓数据不会提交到 GitHub，只保存在本机。

默认路径：

```text
C:\Users\admin\.codex\hermes\fund-manager\portfolio.json
C:\Users\admin\.codex\hermes\fund-manager\portfolio_events.jsonl
```

常用命令：

```powershell
python scripts/portfolio_store.py init
python scripts/portfolio_store.py show
python scripts/portfolio_store.py validate
python scripts/portfolio_store.py merge-snapshot snapshot.json
```

`merge-snapshot` 接收的 JSON 结构参考 `references/portfolio_schema.json`。如果数据来自截图，智能体应先识别截图，生成候选持仓快照，展示新增/删除/变化差异，再在你确认后写入本地文件。

## 报告产物格式

默认情况下，Skill 的报告产物是**聊天内中文 Markdown**，不会自动生成文件。

如果你希望定时任务沉淀报告，可以要求智能体保存文件：

- Markdown：适合继续编辑和后续解析。
- HTML：适合浏览器查看和打印。
- PDF：适合归档和分享，但需要本机安装 Playwright/Chromium。

默认归档目录：

```text
C:\Users\admin\.codex\hermes\fund-manager\reports
```

渲染命令：

```powershell
python scripts/render_report.py report.md --formats md,html --title "Hermes 基金管理报告"
```

生成 PDF：

```powershell
python scripts/render_report.py report.md --formats md,html,pdf --title "Hermes 基金管理报告"
```

如果本机没有 PDF 依赖，先安装：

```powershell
python -m pip install playwright
python -m playwright install chromium
```

建议：定时任务默认只让智能体在聊天中汇报；只有你明确需要归档时，再在 prompt 中加入“同时保存 Markdown/HTML/PDF”。

## 推荐给智能体的测试提示词

### 定时任务建议

```text
交易日 08:45 盘前任务：
使用 $hermes-fund-manager 生成盘前基金与A股简报。请按盘前模式处理：隔夜市场、政策新闻、资金预期、今日主线、我持仓相关方向的风险提示。不要强行汇报盘中涨跌。
```

```text
交易日 10:30 / 14:30 盘中任务：
使用 $hermes-fund-manager 汇报盘中A股整体情况、板块涨跌Top5、我持仓相关方向的涨跌和原因，并给出风险型调整建议。请包含资金面、情绪面、数据验证状态和建议置信度。
```

```text
交易日 15:30 或 16:00 收盘后任务：
使用 $hermes-fund-manager 生成收盘后复盘。请总结今日A股整体表现、板块涨跌Top5、我持仓相关方向表现、原因分析、今日主线、调整建议、建议置信度和数据验证状态。复盘结束后，必须询问我是否要根据最新持仓截图更新本地持仓信息；如果我提供截图，请先识别并展示新增、删除、金额变化、占比变化和板块标签变化的差异，等待我确认后再写入本地。
```

如需 PDF 归档，可把收盘后任务改成：

```text
交易日 15:30 或 16:00 收盘后任务：
使用 $hermes-fund-manager 生成收盘后复盘，并在聊天中汇报。请同时将最终报告保存为 Markdown、HTML 和 PDF 到本地 reports 目录。若 PDF 依赖不可用，请说明原因并至少保留 Markdown/HTML。复盘结束后，必须询问我是否要根据最新持仓截图更新本地持仓信息。
```

```text
非交易日 09:30 或 20:30 任务：
使用 $hermes-fund-manager 生成非交易日基金行业日报。不要汇报不存在的今日行情涨跌；请重点汇总基金行业新闻、政策与监管、产品与资金变化，并检查我的持仓结构风险。
```

### 手动测试提示词

```text
使用 $hermes-fund-manager 汇报今天 A 股整体情况，说明涨幅 Top5 和跌幅 Top5 板块，并给出原因分析和风险提示。
```

```text
使用 $hermes-fund-manager 读取我的本地基金持仓，汇报今天我投资方向的涨跌、原因和调整建议。
```

```text
使用 $hermes-fund-manager 生成今天的基金行业日报。直接在聊天中回答，不要输出文档。
```

```text
使用 $hermes-fund-manager 根据这张截图更新我的基金持仓。请先展示识别结果和差异，不要直接写入。
```

## 验证方式

校验 Skill：

```powershell
$env:PYTHONUTF8='1'
python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\admin\.codex\skills\hermes-fund-manager
```

说明：`SKILL.md` 和参考文档使用中文 UTF-8 内容；在 Windows PowerShell 中运行校验脚本时，建议先设置 `PYTHONUTF8=1`，避免 Python 按系统默认 GBK 解码中文文件。

运行持仓脚本测试：

```powershell
python -m unittest tests.test_portfolio_store -v
```

运行报告渲染测试：

```powershell
python -m unittest tests.test_render_report -v
```

## 隐私约束

不要提交以下内容：

- `portfolio.json`
- `portfolio_events.jsonl`
- 持仓截图
- 生成的报告归档
- API key
- `.env` 文件
- 缓存目录

仓库中的 `.gitignore` 已排除这些私人或生成文件。
