import pathlib
import unittest

FILE=pathlib.Path(__file__).resolve().parents[1]/"app.py"
SOURCE=FILE.read_text(encoding="utf-8")
# Access gate has an earlier stop; identify the independent dashboard's terminal stop.
DEMO_ACTIVE=SOURCE[:SOURCE.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')+250]


class ToolsNavigationPlaceholderTests(unittest.TestCase):
    def test_independent_dashboard_placeholder(self):
        self.assertIn('DEMO_TOOLS_PLACEHOLDER = "Elegir herramienta"',DEMO_ACTIVE)
        self.assertIn('[DEMO_TOOLS_PLACEHOLDER,"Comparar Activos","Simular Compra/Venta"]',DEMO_ACTIVE)
        self.assertIn('if selected!=DEMO_TOOLS_PLACEHOLDER:',DEMO_ACTIVE)
        self.assertIn('st.session_state["demo_tools_nav"]=DEMO_TOOLS_PLACEHOLDER',DEMO_ACTIVE)
        self.assertNotIn('st.radio("Herramientas",["—"',DEMO_ACTIVE)

    def test_ticker_placeholder_intentionally_separate(self):
        self.assertIn('_demo_tickers=["—"]',DEMO_ACTIVE)
        self.assertIn('if selected!="—":',DEMO_ACTIVE)

    def test_independent_demo_ends_before_legacy_dashboard(self):
        self.assertIn('st.stop()', SOURCE[SOURCE.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5'):])
        self.assertLess(SOURCE.index('st.stop()', SOURCE.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')),SOURCE.index('SHEET_ID=PORTFOLIO["sheet_id"]'))


if __name__=="__main__":
    unittest.main()
