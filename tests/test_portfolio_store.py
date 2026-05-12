import json
import tempfile
import unittest
from pathlib import Path

from scripts import portfolio_store


class PortfolioStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_dir = Path(self.temp_dir.name)
        self.portfolio_path = self.store_dir / "portfolio.json"
        self.events_path = self.store_dir / "portfolio_events.jsonl"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_initializes_empty_portfolio(self):
        data = portfolio_store.load_portfolio(self.portfolio_path)

        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["holdings"], [])
        self.assertEqual(data["summary"]["total_amount"], 0)
        self.assertTrue(self.portfolio_path.exists())

    def test_save_and_load_valid_portfolio(self):
        data = portfolio_store.empty_portfolio()
        data["holdings"] = [
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合",
                "amount": 1000.0,
                "weight_percent": 40.0,
                "platform": "天天基金",
                "sector_tags": ["沪深300"],
            },
            {
                "fund_code": "000002",
                "fund_name": "中证医疗指数",
                "amount": 1500.0,
                "weight_percent": 60.0,
                "platform": "支付宝",
                "sector_tags": ["医疗"],
            },
        ]

        portfolio_store.save_portfolio(data, self.portfolio_path)
        loaded = portfolio_store.load_portfolio(self.portfolio_path)

        self.assertEqual(loaded["summary"]["total_amount"], 2500.0)
        self.assertEqual(loaded["summary"]["total_weight_percent"], 100.0)
        self.assertEqual(len(loaded["holdings"]), 2)

    def test_merge_snapshot_returns_diff_and_writes_event(self):
        current = portfolio_store.empty_portfolio()
        current["holdings"] = [
            {
                "fund_code": "000001",
                "fund_name": "华夏成长混合",
                "amount": 1000.0,
                "weight_percent": 100.0,
                "platform": "天天基金",
                "sector_tags": ["消费"],
            }
        ]
        portfolio_store.save_portfolio(current, self.portfolio_path)
        snapshot = {
            "source": "screenshot",
            "holdings": [
                {
                    "fund_code": "000001",
                    "fund_name": "华夏成长混合",
                    "amount": 1200.0,
                    "weight_percent": 50.0,
                    "platform": "天天基金",
                    "sector_tags": ["消费"],
                    "raw_text": "华夏成长混合 1200 50%",
                },
                {
                    "fund_code": "000003",
                    "fund_name": "新能源主题",
                    "amount": 1200.0,
                    "weight_percent": 50.0,
                    "platform": "天天基金",
                    "sector_tags": ["新能源"],
                },
            ],
        }

        diff = portfolio_store.merge_snapshot(snapshot, self.portfolio_path, self.events_path)
        loaded = portfolio_store.load_portfolio(self.portfolio_path)

        self.assertEqual(diff["added"], ["000003"])
        self.assertEqual(diff["removed"], [])
        self.assertEqual(diff["changed"][0]["fund_code"], "000001")
        self.assertEqual(loaded["summary"]["total_amount"], 2400.0)
        events = [json.loads(line) for line in self.events_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(events[0]["diff"]["added"], ["000003"])

    def test_rejects_duplicate_fund_code(self):
        data = portfolio_store.empty_portfolio()
        data["holdings"] = [
            {"fund_code": "000001", "fund_name": "A", "amount": 1, "weight_percent": 50},
            {"fund_code": "000001", "fund_name": "A", "amount": 1, "weight_percent": 50},
        ]

        with self.assertRaisesRegex(portfolio_store.PortfolioError, "duplicate fund_code"):
            portfolio_store.validate_portfolio(data)

    def test_rejects_missing_amount(self):
        data = portfolio_store.empty_portfolio()
        data["holdings"] = [
            {"fund_code": "000001", "fund_name": "A", "weight_percent": 100},
        ]

        with self.assertRaisesRegex(portfolio_store.PortfolioError, "amount"):
            portfolio_store.validate_portfolio(data)

    def test_rejects_weight_percent_not_close_to_100(self):
        data = portfolio_store.empty_portfolio()
        data["holdings"] = [
            {"fund_code": "000001", "fund_name": "A", "amount": 100, "weight_percent": 40},
        ]

        with self.assertRaisesRegex(portfolio_store.PortfolioError, "weight_percent"):
            portfolio_store.validate_portfolio(data)

    def test_rejects_conflicting_names_for_same_code_in_snapshot(self):
        snapshot = {
            "holdings": [
                {"fund_code": "000001", "fund_name": "A", "amount": 50, "weight_percent": 50},
                {"fund_code": "000001", "fund_name": "B", "amount": 50, "weight_percent": 50},
            ]
        }

        with self.assertRaisesRegex(portfolio_store.PortfolioError, "conflicting fund_name"):
            portfolio_store.normalize_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
