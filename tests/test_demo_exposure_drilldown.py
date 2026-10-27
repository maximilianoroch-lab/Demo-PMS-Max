import unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
class DiversificationDrilldown(unittest.TestCase):
 def test_demo_navigation_is_from_active_app(self):
  s=(root/"app.py").read_text(encoding="utf-8")
  active=s[s.index('from demo_independent_model import build_independent_model'):s.index('st.caption("Fuente: Base DEMO PMS Max / DEMO_INVENTARIO_V5')]
  section=active[active.index('elif _demo_page=="Diversificación":'):active.index('elif _demo_page=="Custodia":')]
  self.assertIn('key="demo_exposure_region"',section)
  self.assertIn('key="demo_exposure_sector"',section)
  self.assertIn('_drill=_p.copy()',section)
  self.assertIn('sin atribuir a los ETF sus componentes no verificados',section)
  for page in ("Asesor IA","Comparar","Simulador"):
   self.assertIn('args=(_focus,"'+page+'")',section)
if __name__=="__main__":unittest.main()
