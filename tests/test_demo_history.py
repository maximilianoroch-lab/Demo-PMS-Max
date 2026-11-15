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
 def test_snapshot_uses_buenos_aires_date(self):
  from datetime import datetime
  from zoneinfo import ZoneInfo
  portfolio=pd.DataFrame({"Ticker":["SPY"],"Valor USD_num":[123.0]})
  model={"positions":portfolio,"summary":{"total":123,"positions_count":1}}
  snapshot,_=h.snapshot_frames(model)
  self.assertEqual(snapshot.iloc[0]["Fecha"],str(datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()))
 def test_top15_uses_latest_observed_pair(self):
  p=pd.DataFrame({"Ticker":["AAPL"],"Valor USD_num":[130]})
  history=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-20","2026-10-24"]),"Ticker":["AAPL","AAPL"],"Valor USD":[100,130]})
  result=h.top15_daily(p,history)
  self.assertAlmostEqual(result.iloc[0]["Cambio USD"],30)
 def test_snapshot_rejects_unreconciled_total(self):
  portfolio=pd.DataFrame({"Ticker":["AAPL","SPY"],"Valor USD_num":[100,200]})
  model={"positions":portfolio,"summary":{"total":310,"positions_count":2}}
  with self.assertRaisesRegex(ValueError,"no concilia"):
   h.snapshot_frames(model,"2026-10-24")
 def test_top15_missing_or_zero_previous_is_not_a_return(self):
  positions=pd.DataFrame({"Ticker":["AAPL","SPY","QQQ"],"Valor USD_num":[150,90,80]})
  history=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-23","2026-10-23","2026-10-24","2026-10-24","2026-10-24"]),
   "Ticker":["AAPL","SPY","AAPL","SPY","QQQ"],"Valor USD":[100,0,150,90,80]})
  got=h.top15_daily(positions,history).set_index("Ticker")
  self.assertAlmostEqual(got.loc["AAPL","Cambio %"],50)
  self.assertTrue(pd.isna(got.loc["SPY","Cambio %"]))
  self.assertTrue(pd.isna(got.loc["QQQ","Cambio USD"]))
 def test_daily_total_matches_asset_sum(self):
  portfolio=pd.DataFrame({"Ticker":["AAPL","SPY"],"Valor USD_num":[100,200]})
  model={"positions":portfolio,"summary":{"total":300,"positions_count":2}}
  total,assets=h.snapshot_frames(model,"2026-10-24")
  self.assertAlmostEqual(total.iloc[0]["Patrimonio USD"],assets["Valor USD"].sum())
 def test_no_new_snapshot_if_synthetic_prices_unchanged(self):
  last=pd.DataFrame({"Fecha":["2026-11-12","2026-11-12"],"Ticker":["AAPL","SPY"],"Valor USD":[100,200]})
  today=pd.DataFrame({"Fecha":["2026-11-14","2026-11-14"],"Ticker":["AAPL","SPY"],"Valor USD":[100,200]})
  self.assertFalse(h.has_new_observation(today,last))
 def test_changed_value_or_new_ticker_requires_snapshot(self):
  last=pd.DataFrame({"Fecha":["2026-11-12"],"Ticker":["AAPL"],"Valor USD":[100]})
  changed=pd.DataFrame({"Fecha":["2026-11-14"],"Ticker":["AAPL"],"Valor USD":[100.5]})
  new_ticker=pd.DataFrame({"Fecha":["2026-11-14","2026-11-14"],"Ticker":["AAPL","SPY"],"Valor USD":[100,1]})
  self.assertTrue(h.has_new_observation(changed,last))
  self.assertTrue(h.has_new_observation(new_ticker,last))
 def test_identical_fake_snapshots_appear_as_single_observation(self):
  raw=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-25","2026-10-26","2026-11-14"]),
                    "Patrimonio USD":[1264792.16709]*3,"Instrumentos":[65]*3})
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"snapshot.csv";raw.to_csv(path,index=False)
   with patch.object(h,"HISTORY",path):
    shown=h.load_history()
  self.assertEqual(len(shown),1)
  self.assertEqual(shown.iloc[0]["Fecha"],pd.Timestamp("2026-10-25"))
 def test_changed_then_unchanged_keeps_two_material_observations(self):
  raw=pd.DataFrame({"Fecha":pd.to_datetime(["2026-10-25","2026-10-26","2026-10-27","2026-10-28"]),
                    "Patrimonio USD":[100,100,120,120],"Instrumentos":[2,2,2,2]})
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"snapshot.csv";raw.to_csv(path,index=False)
   with patch.object(h,"HISTORY",path):
    shown=h.load_history()
  self.assertEqual(shown["Patrimonio USD"].tolist(),[100,120])
 def test_asset_histories_collapse_only_identical_full_portfolios(self):
  raw=pd.DataFrame({"Fecha":["2026-10-25","2026-10-25","2026-10-26","2026-10-26","2026-10-27","2026-10-27"],
                    "Ticker":["AAA","BBB"]*3,"Valor USD":[100,50,100,50,110,50]})
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"assets.csv";raw.to_csv(path,index=False)
   with patch.object(h,"ASSETS",path):
    shown=h.load_asset_history()
  self.assertEqual(sorted(shown["Fecha"].dt.strftime("%Y-%m-%d").unique().tolist()),["2026-10-25","2026-10-27"])
if __name__=="__main__":unittest.main()
