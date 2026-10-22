import unittest
import pandas as pd
from demo_independent_model import build_independent_model, CUSTODIANS

def sample():
    rows=[]
    for i,t in enumerate(["AAPL","SPY","GGAL","GD35","BTC","CASH"]):
        r={"Ticker":t,"Cantidad total":100,"Precio USD indicativo":10,"Valor USD indicativo":1000}
        r.update({c:0 for c in CUSTODIANS})
        r[CUSTODIANS[i]]=100
        rows.append(r)
    return pd.DataFrame(rows)

class IndependentModelTests(unittest.TestCase):
    def test_reject_partial_inventory(self):
        with self.assertRaisesRegex(ValueError,"incompleto"):build_independent_model(sample())
    def test_reject_custody_mismatch(self):
        a=sample()
        a.loc[0,"Cantidad total"]=101
        with self.assertRaises(ValueError):build_independent_model(a)
    def test_reject_duplicate_tickers(self):
        a=pd.concat([sample()]*11,ignore_index=True).iloc[:65]
        with self.assertRaises(ValueError):build_independent_model(a)

if __name__=="__main__":unittest.main()
