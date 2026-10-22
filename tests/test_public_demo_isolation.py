"""Asegura que la versión pública no llegue a cargar feeds heredados."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PublicDemoIsolationTests(unittest.TestCase):
    def test_app_syntax(self):
        ast.parse((ROOT/"app.py").read_text(encoding="utf-8"))
    def test_public_entrypoint_stops_before_legacy_feed(self):
        src=(ROOT/"app.py").read_text(encoding="utf-8")
        begin=src.index('from demo_independent_model import build_independent_model')
        stop=src.index('st.markdown("""\\n<style>') if 'st.markdown("""\\n<style>' in src else src.index('st.markdown("""\n<style>')
        self.assertLess(begin,stop)
        self.assertIn("st.stop()",src[begin:stop])
        self.assertGreater(src.index("data=get_data()"),stop)
    def test_no_scaled_mode(self):
        config=(ROOT/"portfolio_config.py").read_text(encoding="utf-8")
        data=(ROOT/"data.py").read_text(encoding="utf-8")
        self.assertIn('"data_mode": "independent"',config)
        self.assertIn('"history_mode": "none"',config)
        self.assertNotIn("DEMO_MULTIPLIER",data)
        self.assertNotIn("demo_legacy_scaled",data)

if __name__=="__main__":
    unittest.main()
