# 天天基金数据优先级

当本机存在 `TTFUND_APIKEY` 时，优先使用天天基金 Skill。若缺少该环境变量，停止天天基金调用，并提示用户：

`当前未检测到 TTFUND_APIKEY，请先前往天天基金搜索 skills 获取 apikey，并在本机配置该环境变量后重试。`

统一网关：

- URL：`https://skills.tiantianfunds.com/ai-smart-skill-service/openapi/skill/invoke`
- Method：`POST`
- Header：`X-API-Key: $TTFUND_APIKEY`
- Body 必须包含 `skill_id` 和 `_skill_version`

## 常用 Skill

| 用途 | skill_id | version | 使用场景 |
| --- | --- | --- | --- |
| 基金详情 | `FUND_BASE_INFOS` | `1.2.0` | 基金档案、分类、业绩基准、交易规则、历史净值上下文 |
| 基金持仓 | `FUND_HOLDING_INFO` | `1.0.0` | 重仓股债、行业配置、仓位信息 |
| 基金净值 | `FUND_NAV_INFO` | `1.0.0` | 单日净值、累计净值、日涨跌幅、分红拆分事件 |
| 指数行情 | `FUND_INDEX_INFO` | `1.0.0` | 指数行情、估值、成分、表现、相关产品 |
| 基金搜索 | `FUND_SEARCH` | `1.0.0` | 查询基金、指数、基金经理、投顾策略候选 |
| 条件选基 | `FUND_CONDITION_SELECT` | `1.1.0` | 基金筛选和排序；不能当作全市场 A 股板块排行榜 |

## 能力边界

天天基金适合查询已知基金、指数和基金相关实体。当前 Skill 清单没有“全市场板块涨跌排行榜”能力。

因此：

- 基金/指数/持仓相关数据优先天天基金。
- “A 股所有板块涨幅 Top5 / 跌幅 Top5”使用东方财富板块行情，并在报告中标注来源。

## 兜底规则

如果天天基金请求失败、超时或返回数据不可用：

1. 只在必要时使用结构化行情或网络搜索兜底。
2. 在受影响章节标注数据来源。
3. 报告结尾附上：`本次部分数据因天天基金接口不可用，使用网络搜索/其他公开行情源兜底。`
