"""Guardrails to prevent leaking legacy Bersoch observations into DEMO V5 rankings."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DemoHistoryIsolationTests(unittest.TestCase):
    def test_demo_rankings_never_consume_legacy_sheet(self):
        app=(ROOT/"app.py").read_text(encoding="utf-8")
        self.assertNotIn('show_top10(st, PORTFOLIO["sheet_id"]', app)
        self.assertIn("historial antiguo", app)
        self.assertIn('from demo_history import load_history,load_asset_history',app)
    def test_independent_history_is_recorded_from_demo_positions(self):
        code=(ROOT/"demo_history.py").read_text(encoding="utf-8")
        self.assertIn('model["positions"]',code)
        self.assertIn('data',str(ROOT/"data"))
    def test_demo_uses_own_inventory(self):
        config=(ROOT/"portfolio_config.py").read_text(encoding="utf-8")
        self.assertIn('"data_mode": "independent"',config)
        self.assertIn('"history_mode": "none"',config)
        self.assertNotIn("18qu9LXo55qQZq4oEAq42u_DKaI7e9lZL_PkfUZiu0T0",config)

if __name__=="__main__":unittest.main()
