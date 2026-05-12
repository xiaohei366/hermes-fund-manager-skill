# Tiantian Fund Data Priority

Use Tiantian Fund skills when `TTFUND_APIKEY` is present. If it is missing, stop Tiantian calls and tell the user:

`当前未检测到 TTFUND_APIKEY，请先前往天天基金搜索 skills 获取 apikey，并在本机配置该环境变量后重试。`

Gateway:

- URL: `https://skills.tiantianfunds.com/ai-smart-skill-service/openapi/skill/invoke`
- Method: `POST`
- Header: `X-API-Key: $TTFUND_APIKEY`
- Body must include `skill_id` and `_skill_version`.

## Useful Skills

| Purpose | skill_id | version | Use |
| --- | --- | --- | --- |
| Fund details | `FUND_BASE_INFOS` | `1.2.0` | Fund profile, classification, benchmark, trading rules, historical NAV context |
| Fund holdings | `FUND_HOLDING_INFO` | `1.0.0` | Heavy stocks/bonds, industry allocation, position data |
| Fund NAV | `FUND_NAV_INFO` | `1.0.0` | Daily NAV, accumulated NAV, daily return, dividend/split events |
| Index info | `FUND_INDEX_INFO` | `1.0.0` | Index quote, valuation, composition, performance, related products |
| Fund search | `FUND_SEARCH` | `1.0.0` | Resolve fund/index/manager/strategy candidates before detail calls |
| Condition select | `FUND_CONDITION_SELECT` | `1.1.0` | Fund screening and ranking; not a full A-share sector ranking source |

## Boundary

Tiantian Fund can query known indexes and fund-related entities, but the current skill list does not expose a full market sector quote ranking. For "all A-share sectors Top 5 gainers/losers", use Eastmoney sector quotes and label the source.

## Fallback

If a Tiantian request fails, times out, or returns unusable data:

1. Continue with structured fallback data only when needed.
2. Clearly mark the affected section.
3. End the report with: `本次部分数据因天天基金接口不可用，使用网络搜索/其他公开行情源兜底。`
