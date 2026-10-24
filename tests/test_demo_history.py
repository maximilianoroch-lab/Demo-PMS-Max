import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import demo_history as h

class DemoHistoryTests(unittest.TestCase):
 def test_one_snapshot_per_day(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"snapshot.csv"
   first=pd.DataFrame([{"Fecha":"2026-10-24","Patrimonio USD":100}])
   second=pd.DataFrame([{"Fecha":"2026-10-24","Patrimonio USD":110}])
   h.upsert_csv(first,path,["Fecha"])
   result=h.upsert_csv(second,path,["Fecha"])
   self.assertEqual(len(result),1)
   self.assertEqual(result.iloc[0]["Patrimonio USD"],110)
 def test_top15_change_only_with_two_observations(self):
  portfolio=pd.DataFrame({"Ticker":["AAPL","SPY"],"Valor USD_num":[110,200]})
  day=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-24","2026-10-24"]),
       "Ticker":["AAPL","SPY"],"Valor USD":[110,200]})
  initial=h.top15_daily(portfolio,day)
  self.assertTrue(pd.isna(initial.iloc[0]["Cambio USD"]))
  previous=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-23","2026-10-23"]),
       "Ticker":["AAPL","SPY"],"Valor USD":[100,200]})
  result=h.top15_daily(portfolio,pd.concat([day,previous]))
  a=result.set_index("Ticker").loc["AAPL"]
  self.assertAlmostEqual(a["Cambio USD"],10)
  self.assertAlmostEqual(a["Cambio %"],10)
 def test_daily_total_matches_asset_sum(self):
  portfolio=pd.DataFrame({"Ticker":["AAPL","SPY"],"Valor USD_num":[100,200]})
  model={"positions":portfolio,"summary":{"total":300,"positions_count":2}}
  total,assets=h.snapshot_frames(model,"2026-10-24")
  self.assertAlmostEqual(total.iloc[0]["Patrimonio USD"],assets["Valor USD"].sum())
if __name__=="__main__":unittest.main()
