"""Controles para prevenir la mezcla accidental de carteras."""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
REAL_SHEET_ID = "18qu9LXo55qQZq4oEAq42u_DKaI7e9lZL_PkfUZiu0T0"

class PortfolioIsolationTests(unittest.TestCase):
    def test_demo_does_not_use_real_base(self):
        config = (ROOT / "portfolio_config.py").read_text(encoding="utf-8")
        tree = ast.parse(config)
        data = next(node.value for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id=="PORTFOLIO" for t in node.targets))
        # literal config, no external imports or access tokens needed
        settings = ast.literal_eval(data)
        self.assertNotEqual(settings["sheet_id"], REAL_SHEET_ID)
        self.assertEqual(settings["id"], "demo_pms_max")
        self.assertEqual(settings["display_name"], "DEMO PMS Max")

    def test_independent_mode_has_no_scaling(self):
        code = (ROOT / "data.py").read_text(encoding="utf-8")
        self.assertIn('if DATA_MODE == "demo_legacy_scaled" else 1.0', code)
        self.assertIn('"history_mode") == "none"', code)
        self.assertIn('optional_feeds', code)

    def test_all_python_files_compile(self):
        for name in ("data.py", "app.py", "advisor.py", "portfolio_config.py"):
            with self.subTest(name=name):
                compile((ROOT/name).read_text(encoding="utf-8"), str(ROOT/name), "exec")

if __name__ == "__main__":
    unittest.main()
