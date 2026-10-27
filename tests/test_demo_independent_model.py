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
    def test_group_totals_reconcile(self):
        result=build_independent_model(sample())
        total=result["summary"]["total"]
        for group in ("by_type","by_region","by_custodian","by_sector"):
            self.assertAlmostEqual(result[group]["Valor USD_num"].sum(),total)
        self.assertAlmostEqual(result["summary"]["crypto"]+result["summary"]["non_crypto"],total)
        self.assertAlmostEqual(result["positions"]["Peso_num"].sum(),1.0)
    def test_regional_exposures_are_not_generic(self):
        result=build_independent_model(sample())
        positions=result["positions"].set_index("Ticker")
        self.assertEqual(positions.loc["SPY","Región directa"],"Estados Unidos")
        self.assertEqual(positions.loc["FXI","Región directa"],"China")
        self.assertEqual(positions.loc["BTC","Región directa"],"Cripto global")
        self.assertEqual(positions.loc["GGAL","Región directa"],"Argentina")
    def test_decimal_comma_in_values(self):
        raw=sample()
        raw["Precio USD indicativo"]=raw["Precio USD indicativo"].astype(str)
        raw.loc[0,"Precio USD indicativo"]="10,5"
        raw.loc[0,"Valor USD indicativo"]=1050
        result=build_independent_model(raw)
        self.assertAlmostEqual(result["summary"]["total"],65050)
    def test_reject_missing_price(self):
        a=sample()
        a.loc[0,"Precio USD indicativo"]=float("nan")
        with self.assertRaisesRegex(ValueError,"no finitos"):
            build_independent_model(a)
    def test_reject_partial_inventory(self):
        with self.assertRaisesRegex(ValueError,"incompleto"):build_independent_model(sample().iloc[:-1])
    def test_reject_custody_mismatch(self):
        a=sample()
        a.loc[0,"Cantidad total"]=101
        with self.assertRaises(ValueError):build_independent_model(a)
    def test_reject_duplicate_tickers(self):
        a=sample()
        a.loc[1,"Ticker"]=a.loc[0,"Ticker"]
        with self.assertRaises(ValueError):build_independent_model(a)

if __name__=="__main__":unittest.main()
