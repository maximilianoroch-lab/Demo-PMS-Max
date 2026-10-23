import unittest
import pandas as pd
from demo_independent_model import build_independent_model, CUSTODIANS

def sample():
    from demo_independent_model import ETF, ARG, BONDS, CRYPTO, US
    tickers=sorted(ETF | ARG | BONDS | CRYPTO | US | {"CASH"})
    if len(tickers)<65:
        raise AssertionError("No hay suficientes instrumentos para construir un inventario válido")
    rows=[]
    for i,t in enumerate(tickers[:65]):
        r={"Ticker":t,"Cantidad total":100,"Precio USD indicativo":10,
           "Valor USD indicativo":1000}
        r.update({c:0 for c in CUSTODIANS})
        r[CUSTODIANS[i % len(CUSTODIANS)]]=100
        rows.append(r)
    return pd.DataFrame(rows)

class IndependentModelTests(unittest.TestCase):
    def test_accept_complete_inventory(self):
        result=build_independent_model(sample())
        self.assertEqual(result["summary"]["positions_count"],65)
        self.assertAlmostEqual(result["summary"]["total"],65000)
    def test_reject_partial_inventory(self):
        with self.assertRaisesRegex(ValueError,"incompleto"):build_independent_model(sample().iloc[:-1])
    def test_reject_custody_mismatch(self):
        a=sample()
        a.loc[0,"Cantidad total"]=101
        with self.assertRaises(ValueError):build_independent_model(a)
    def test_reject_duplicate_tickers(self):
        a=pd.concat([sample()]*11,ignore_index=True).iloc[:65]
        with self.assertRaises(ValueError):build_independent_model(a)

if __name__=="__main__":unittest.main()
