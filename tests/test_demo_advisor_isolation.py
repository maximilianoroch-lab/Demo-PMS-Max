"""Regresión: Asesor DEMO sólo recibe cartera ficticia V5."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class DemoAdvisorIsolation(unittest.TestCase):
 def test_python_syntax(self):
  for file in ("app.py","advisor.py","demo_independent_model.py"):
   ast.parse((ROOT/file).read_text(encoding="utf-8"),filename=file)
 def test_advisor_adapter_precedes_legacy_data(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  gate=code[code.index('from demo_independent_model import build_independent_model'):code.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')]
  self.assertIn('elif _demo_page=="Asesor IA":',gate)
  self.assertIn('"app_feed_v2":_app',gate)
  self.assertIn('"looker_feed_v2":_p.copy()',gate)
  self.assertIn('ask_advisor(_intro+_question,_advisor_data,_p',gate)
  self.assertNotIn('data=get_data()',gate)
  self.assertIn('st.stop()',code[code.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5'):code.index('data=get_data()')])
 def test_advisor_no_real_holdings_rules(self):
  code=(ROOT/"advisor.py").read_text(encoding="utf-8")
  self.assertIn('inventario ficticio DEMO V5',code)
  self.assertNotIn('FUT se integra a Crypto',code)
if __name__=="__main__":unittest.main()
