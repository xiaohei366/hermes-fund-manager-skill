#!/usr/bin/env python3
"""Local portfolio persistence helpers for the Hermes fund manager skill."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STORE_DIR = Path.home() / ".codex" / "hermes" / "fund-manager"
DEFAULT_PORTFOLIO_PATH = DEFAULT_STORE_DIR / "portfolio.json"
DEFAULT_EVENTS_PATH = DEFAULT_STORE_DIR / "portfolio_events.jsonl"
WEIGHT_TOLERANCE = 0.5


class PortfolioError(ValueError):
    """Raised when local portfolio data is invalid or ambiguous."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_portfolio() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "owner": "local",
        "currency": "CNY",
        "updated_at": None,
        "source": "manual",
        "summary": {
            "total_amount": 0,
            "total_weight_percent": 0,
            "holding_count": 0,
        },
        "holdings": [],
    }


def load_portfolio(path: str | Path | None = None) -> dict[str, Any]:
    portfolio_path = Path(path) if path else DEFAULT_PORTFOLIO_PATH
    if not portfolio_path.exists():
        data = empty_portfolio()
        save_portfolio(data, portfolio_path)
        return data

    data = json.loads(portfolio_path.read_text(encoding="utf-8"))
    validate_portfolio(data)
    return summarize_portfolio(data)


def save_portfolio(data: dict[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    portfolio_path = Path(path) if path else DEFAULT_PORTFOLIO_PATH
    portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = summarize_portfolio(deepcopy(data))
    validate_portfolio(normalized)
    portfolio_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalized


def validate_portfolio(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise PortfolioError("schema_version must be 1")
    holdings = data.get("holdings")
    if not isinstance(holdings, list):
        raise PortfolioError("holdings must be a list")

    seen_codes: set[str] = set()
    total_weight = 0.0
    for index, holding in enumerate(holdings):
        if not isinstance(holding, dict):
            raise PortfolioError(f"holding at index {index} must be an object")
        fund_code = _required_text(holding, "fund_code", index)
        _required_text(holding, "fund_name", index)
        amount = _required_number(holding, "amount", index)
        weight = _required_number(holding, "weight_percent", index)
        if amount < 0:
            raise PortfolioError(f"amount must be non-negative for {fund_code}")
        if weight < 0:
            raise PortfolioError(f"weight_percent must be non-negative for {fund_code}")
        if fund_code in seen_codes:
            raise PortfolioError(f"duplicate fund_code: {fund_code}")
        seen_codes.add(fund_code)
        total_weight += weight

    if holdings and abs(total_weight - 100.0) > WEIGHT_TOLERANCE:
        raise PortfolioError(
            f"total weight_percent must be close to 100, got {round(total_weight, 4)}"
        )


def normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise PortfolioError("snapshot must be an object")
    holdings = snapshot.get("holdings")
    if not isinstance(holdings, list):
        raise PortfolioError("snapshot.holdings must be a list")

    by_code: dict[str, dict[str, Any]] = {}
    for index, raw_holding in enumerate(holdings):
        if not isinstance(raw_holding, dict):
            raise PortfolioError(f"snapshot holding at index {index} must be an object")
        holding = _normalize_holding(raw_holding, index)
        fund_code = holding["fund_code"]
        previous = by_code.get(fund_code)
        if previous and previous["fund_name"] != holding["fund_name"]:
            raise PortfolioError(f"conflicting fund_name for fund_code {fund_code}")
        if previous:
            raise PortfolioError(f"duplicate fund_code: {fund_code}")
        by_code[fund_code] = holding

    normalized = empty_portfolio()
    normalized["source"] = str(snapshot.get("source") or "screenshot")
    normalized["updated_at"] = utc_now()
    normalized["holdings"] = sorted(by_code.values(), key=lambda item: item["fund_code"])
    return summarize_portfolio(normalized)


def merge_snapshot(
    snapshot: dict[str, Any],
    portfolio_path: str | Path | None = None,
    events_path: str | Path | None = None,
) -> dict[str, Any]:
    current = load_portfolio(portfolio_path)
    incoming = normalize_snapshot(snapshot)
    diff = build_diff(current, incoming)
    save_portfolio(incoming, portfolio_path)
    append_event(
        {
            "event": "portfolio_update",
            "created_at": utc_now(),
            "source": incoming["source"],
            "diff": diff,
            "summary": incoming["summary"],
        },
        events_path,
    )
    return diff


def build_diff(current: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    current_by_code = {item["fund_code"]: item for item in current.get("holdings", [])}
    incoming_by_code = {item["fund_code"]: item for item in incoming.get("holdings", [])}
    current_codes = set(current_by_code)
    incoming_codes = set(incoming_by_code)

    changed = []
    for code in sorted(current_codes & incoming_codes):
        before = current_by_code[code]
        after = incoming_by_code[code]
        field_changes = {}
        for field in ("fund_name", "amount", "weight_percent", "platform", "sector_tags"):
            if before.get(field) != after.get(field):
                field_changes[field] = {"before": before.get(field), "after": after.get(field)}
        if field_changes:
            changed.append({"fund_code": code, "changes": field_changes})

    return {
        "added": sorted(incoming_codes - current_codes),
        "removed": sorted(current_codes - incoming_codes),
        "changed": changed,
    }


def append_event(event: dict[str, Any], path: str | Path | None = None) -> None:
    events_path = Path(path) if path else DEFAULT_EVENTS_PATH
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def summarize_portfolio(data: dict[str, Any]) -> dict[str, Any]:
    holdings = data.setdefault("holdings", [])
    for index, holding in enumerate(holdings):
        holdings[index] = _normalize_holding(holding, index)
    total_amount = round(sum(item["amount"] for item in holdings), 4)
    total_weight = round(sum(item["weight_percent"] for item in holdings), 4)
    data["summary"] = {
        "total_amount": total_amount,
        "total_weight_percent": total_weight,
        "holding_count": len(holdings),
    }
    data.setdefault("schema_version", 1)
    data.setdefault("owner", "local")
    data.setdefault("currency", "CNY")
    data.setdefault("source", "manual")
    data.setdefault("updated_at", None)
    return data


def _normalize_holding(raw_holding: dict[str, Any], index: int) -> dict[str, Any]:
    holding = {
        "fund_code": _required_text(raw_holding, "fund_code", index),
        "fund_name": _required_text(raw_holding, "fund_name", index),
        "amount": round(_required_number(raw_holding, "amount", index), 4),
        "weight_percent": round(_required_number(raw_holding, "weight_percent", index), 4),
        "platform": str(raw_holding.get("platform") or "unknown").strip() or "unknown",
        "sector_tags": _normalize_tags(raw_holding.get("sector_tags")),
    }
    if raw_holding.get("raw_text"):
        holding["raw_text"] = str(raw_holding["raw_text"]).strip()
    return holding


def _required_text(data: dict[str, Any], field: str, index: int) -> str:
    value = data.get(field)
    if value is None or str(value).strip() == "":
        raise PortfolioError(f"{field} is required for holding at index {index}")
    return str(value).strip()


def _required_number(data: dict[str, Any], field: str, index: int) -> float:
    if field not in data or data[field] in (None, ""):
        raise PortfolioError(f"{field} is required for holding at index {index}")
    try:
        return float(str(data[field]).replace(",", ""))
    except ValueError as exc:
        raise PortfolioError(f"{field} must be numeric for holding at index {index}") from exc


def _normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_tags = value.split(",")
    elif isinstance(value, list):
        raw_tags = value
    else:
        raise PortfolioError("sector_tags must be a list or comma-separated string")
    return sorted({str(tag).strip() for tag in raw_tags if str(tag).strip()})


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage local Hermes fund portfolio data.")
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO_PATH)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init")
    subparsers.add_parser("show")
    subparsers.add_parser("validate")
    merge_parser = subparsers.add_parser("merge-snapshot")
    merge_parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()

    if args.command == "init":
        data = load_portfolio(args.portfolio)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.command == "show":
        data = load_portfolio(args.portfolio)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate":
        data = load_portfolio(args.portfolio)
        validate_portfolio(data)
        print("portfolio is valid")
        return 0
    if args.command == "merge-snapshot":
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        diff = merge_snapshot(snapshot, args.portfolio, args.events)
        print(json.dumps(diff, ensure_ascii=False, indent=2))
        return 0
    raise PortfolioError(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
