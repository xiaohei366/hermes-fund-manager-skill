import tempfile
import unittest
from pathlib import Path

from scripts import render_report


class RenderReportTests(unittest.TestCase):
    def test_markdown_to_html_renders_common_report_elements(self):
        markdown = "# 市场概览\n\n| 板块 | 涨跌幅 |\n| --- | --- |\n| AI | +2.3% |\n\n- 风险提示\n"

        html = render_report.markdown_to_html(markdown, title="测试报告")

        self.assertIn("<title>测试报告</title>", html)
        self.assertIn("<h1>市场概览</h1>", html)
        self.assertIn("<table>", html)
        self.assertIn("<td>AI</td>", html)
        self.assertIn("<li>风险提示</li>", html)

    def test_write_artifacts_creates_markdown_and_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            markdown = "# 收盘后复盘\n\n内容"

            result = render_report.write_artifacts(
                markdown,
                output_dir=output_dir,
                basename="report",
                title="收盘后复盘",
                formats=["md", "html"],
            )

            self.assertEqual(result["md"], output_dir / "report.md")
            self.assertEqual(result["html"], output_dir / "report.html")
            self.assertTrue((output_dir / "report.md").exists())
            self.assertTrue((output_dir / "report.html").exists())
            self.assertIn("<h1>收盘后复盘</h1>", (output_dir / "report.html").read_text(encoding="utf-8"))

    def test_rejects_unknown_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(render_report.RenderReportError, "unknown format"):
                render_report.write_artifacts(
                    "# 报告",
                    output_dir=Path(temp_dir),
                    basename="report",
                    title="报告",
                    formats=["docx"],
                )


if __name__ == "__main__":
    unittest.main()
