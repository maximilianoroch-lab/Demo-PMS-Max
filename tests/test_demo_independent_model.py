import unittest
import pandas as pd
from demo_independent_model import build_independent_model

def sample():
 return pd.DataFrame([
 {"Cuenta DEMO":"DEMO-BROKER-01","Ticker":"AAPL","Cantidad":2,"Valor DEMO USD":400},
 {"Cuenta DEMO":"DEMO-BROKER-02","Ticker":"GD35","Cantidad":100,"Valor DEMO USD":70},
 {"Cuenta DEMO":"DEMO-BANK-01","Ticker":"CASH","Cantidad":30,"Valor DEMO USD":30},
 ])

class IndependentModelTests(unittest.TestCase):
 def test_total_and_components_reconcile(self):
  m=build_independent_model(sample())
  self.assertEqual(m["summary"]["total"],500)
  self.assertAlmostEqual(m["positions"]["Peso_num"].sum(),1)
  for key in ("by_type","by_region","by_custodian"):
   self.assertAlmostEqual(m[key]["Valor USD_num"].sum(),500)
 def test_argentina_risk_from_fictitious_positions(self):
  m=build_independent_model(sample())
  self.assertAlmostEqual(m["summary"]["argentina_pct"],70/500)
 def test_reject_unknown_ticker(self):
  x=sample()
  x.loc[0,"Ticker"]="UNKNOWN"
  with self.assertRaises(ValueError): build_independent_model(x)
 def test_reject_unknown_custodian(self):
  x=sample()
  x.loc[0,"Cuenta DEMO"]="REAL ACCOUNT"
  with self.assertRaises(ValueError): build_independent_model(x)
 def test_reject_zero_total(self):
  x=sample()
  x["Valor DEMO USD"]=0
  with self.assertRaises(ValueError): build_independent_model(x)

if __name__=="__main__": unittest.main()
