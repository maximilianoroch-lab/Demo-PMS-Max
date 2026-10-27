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
 def test_ticker_change_resets_context(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  self.assertIn('st.session_state["demo_advisor_symbol"]=_selected',code)
  self.assertIn('st.session_state.pop("demo_advisor_answer",None)',code)
  self.assertIn('st.session_state["demo_advisor_question"]=',code)
  self.assertIn('st.text_input("Símbolo de mercado",key="demo_advisor_symbol")',code)
  self.assertIn('on_change=_demo_active_ticker_changed',code)
  self.assertIn('st.session_state.pop("demo_advisor_ticker",None)',code)
  self.assertIn('st.session_state.pop("demo_technical_data",None)',code)
 def test_technical_indicator_parity(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  active=code[code.index('elif _demo_page=="Asesor IA":'):code.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')]
  self.assertIn('_rsi_fig.add_hline(y=70',active)
  self.assertIn('_rsi_fig.add_hline(y=30',active)
  self.assertIn('_rsi_fig.update_yaxes(range=[0,100])',active)
  self.assertIn('if not _history_symbol:',active)
  self.assertIn('st.session_state.pop("demo_technical_data",None)',active)
 def test_market_symbol_mismatch_is_visible(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  active=code[code.index('elif _demo_page=="Asesor IA":'):code.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')]
  self.assertIn('if _history_symbol and _history_symbol!=_selected:',active)
  self.assertIn('el Asesor IA no recibirá estos indicadores',active)
  self.assertIn('technical_snapshot=_snapshot',active)
 def test_fundamental_comparison_uses_demo_only(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  active=code[code.index('from demo_independent_model import build_independent_model'):code.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')]
  section=active[active.index('elif _demo_page=="Comparar":'):active.index('elif _demo_page=="Simulador":')]
  self.assertIn('compare_companies_structured(',section)
  self.assertIn('"app_feed_v2":_cmp_app',section)
  self.assertIn('"looker_feed_v2":_p.copy()',section)
  for field in ("period_a","period_b","source_a","source_b"):
   self.assertIn('_metric.get("'+field+'")',section)
  self.assertIn('st.session_state.pop("demo_fundamental_result",None)',section)
  self.assertNotIn('get_data()',section)
 def test_cross_module_navigation(self):
  code=(ROOT/"app.py").read_text(encoding="utf-8")
  self.assertIn('def _demo_open_ticker(ticker,page):',code)
  for page in ('Asesor IA','Comparar','Simulador'):
   self.assertIn('args=(_focus,"'+page+'")',code)
  self.assertIn('st.session_state["demo_sidebar_ticker"]=ticker',code)
  self.assertIn('disabled=not _focus_options',code)
 def test_advisor_no_real_holdings_rules(self):
  code=(ROOT/"advisor.py").read_text(encoding="utf-8")
  self.assertIn('inventario ficticio DEMO V5',code)
  self.assertNotIn('FUT se integra a Crypto',code)
if __name__=="__main__":unittest.main()
