#!/usr/bin/env python3
"""Render Hermes fund reports to Markdown, HTML, and optionally PDF."""

from __future__ import annotations

import argparse
import html
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable


DEFAULT_REPORT_DIR = Path.home() / ".codex" / "hermes" / "fund-manager" / "reports"
ALLOWED_FORMATS = {"md", "html", "pdf"}


class RenderReportError(ValueError):
    """Raised when report rendering cannot continue."""


def safe_basename(value: str | None = None) -> str:
    if value:
        cleaned = re.sub(r"[^0-9A-Za-z._-]+", "-", value.strip()).strip("-")
        if cleaned:
            return cleaned
    return "fund-report-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def markdown_to_html(markdown: str, title: str = "Hermes 基金管理报告") -> str:
    body = render_blocks(markdown)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      color: #172033;
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
      line-height: 1.65;
      margin: 36px auto;
      max-width: 920px;
      padding: 0 28px;
    }}
    h1, h2, h3 {{ color: #111827; line-height: 1.3; }}
    h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
    table {{ border-collapse: collapse; margin: 18px 0; width: 100%; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }}
    th {{ background: #f3f4f6; }}
    blockquote {{
      border-left: 4px solid #94a3b8;
      color: #475569;
      margin: 16px 0;
      padding-left: 14px;
    }}
    code {{ background: #f3f4f6; border-radius: 4px; padding: 1px 4px; }}
    .risk {{ color: #991b1b; font-weight: 600; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def render_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    chunks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph:
            chunks.append("<p>" + "<br>".join(html.escape(line) for line in paragraph) + "</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            chunks.append("<ul>" + "".join(f"<li>{item}</li>" for item in list_items) + "</ul>")
            list_items.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            index += 1
            continue
        if stripped.startswith("|") and _looks_like_table(lines, index):
            flush_paragraph()
            flush_list()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            chunks.append(_render_table(table_lines))
            continue
        if stripped.startswith("#"):
            flush_paragraph()
            flush_list()
            level = min(len(stripped) - len(stripped.lstrip("#")), 3)
            text = stripped[level:].strip()
            chunks.append(f"<h{level}>{html.escape(text)}</h{level}>")
            index += 1
            continue
        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            list_items.append(html.escape(stripped[2:].strip()))
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            flush_list()
            chunks.append(f"<blockquote>{html.escape(stripped[1:].strip())}</blockquote>")
            index += 1
            continue
        paragraph.append(line)
        index += 1

    flush_paragraph()
    flush_list()
    return "\n".join(chunks)


def _looks_like_table(lines: list[str], index: int) -> bool:
    return index + 1 < len(lines) and bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1]))


def _render_table(lines: list[str]) -> str:
    rows = [_split_table_row(line) for line in lines]
    if len(rows) < 2:
        return ""
    header = rows[0]
    body_rows = rows[2:]
    head_html = "".join(f"<th>{html.escape(cell)}</th>" for cell in header)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in body_rows
    )
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table>"


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def write_artifacts(
    markdown: str,
    output_dir: Path = DEFAULT_REPORT_DIR,
    basename: str | None = None,
    title: str = "Hermes 基金管理报告",
    formats: Iterable[str] = ("md", "html"),
) -> dict[str, Path]:
    selected_formats = [fmt.lower().strip() for fmt in formats]
    unknown = sorted(set(selected_formats) - ALLOWED_FORMATS)
    if unknown:
        raise RenderReportError(f"unknown format: {', '.join(unknown)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    base = safe_basename(basename)
    result: dict[str, Path] = {}
    html_path: Path | None = None

    if "md" in selected_formats:
        md_path = output_dir / f"{base}.md"
        md_path.write_text(markdown, encoding="utf-8")
        result["md"] = md_path

    if "html" in selected_formats or "pdf" in selected_formats:
        html_path = output_dir / f"{base}.html"
        html_path.write_text(markdown_to_html(markdown, title=title), encoding="utf-8")
        result["html"] = html_path

    if "pdf" in selected_formats:
        if html_path is None:
            raise RenderReportError("html artifact is required before pdf rendering")
        pdf_path = output_dir / f"{base}.pdf"
        render_pdf(html_path, pdf_path)
        result["pdf"] = pdf_path

    return result


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise RenderReportError(
            "PDF 生成需要安装 Playwright：python -m pip install playwright && python -m playwright install chromium"
        ) from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.pdf(path=str(pdf_path), format="A4", print_background=True, margin={"top": "16mm", "right": "14mm", "bottom": "16mm", "left": "14mm"})
        browser.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Hermes fund report Markdown into artifacts.")
    parser.add_argument("input", type=Path, help="Markdown report file to render")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--basename", default=None)
    parser.add_argument("--title", default="Hermes 基金管理报告")
    parser.add_argument("--formats", default="md,html", help="Comma-separated formats: md,html,pdf")
    args = parser.parse_args()

    markdown = args.input.read_text(encoding="utf-8")
    formats = [item.strip() for item in args.formats.split(",") if item.strip()]
    artifacts = write_artifacts(
        markdown,
        output_dir=args.output_dir,
        basename=args.basename or args.input.stem,
        title=args.title,
        formats=formats,
    )
    for fmt, path in artifacts.items():
        print(f"{fmt}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
