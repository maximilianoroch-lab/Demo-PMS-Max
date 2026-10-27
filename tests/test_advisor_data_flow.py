"""Ejecución real y offline del contexto de IA, exclusivamente con cartera ficticia."""
import unittest
import pandas as pd
from advisor import compact, eligible_technical_snapshot, describe_technical_snapshot

class AdvisorDataFlow(unittest.TestCase):
    def setUp(self):
        self.demo=pd.DataFrame([
            {"Ticker":"AAPL","Nombre":"Apple DEMO","Valor USD_num":100.0,"Peso_num":.25,"Tipo":"Cedear","Clase":"Renta variable","Región":"Estados Unidos","Sector":"Tecnología","Cuenta":"FICTICIA-1","Custodio":"Ficticio","Peso cartera_num":.25},
            {"Ticker":"SPY","Nombre":"ETF DEMO","Valor USD_num":300.0,"Peso_num":.75,"Tipo":"ETF","Clase":"Renta variable","Región":"Estados Unidos","Sector":"ETF","Cuenta":"FICTICIA-2","Custodio":"Ficticio","Peso cartera_num":.75},
        ])
        self.feed={"app_feed_v2":self.demo.copy(),"looker_feed_v2":self.demo.copy(),"dashboard_riesgo_v2":pd.DataFrame(),"dashboard_exposicion_v2":pd.DataFrame()}
    def test_context_contains_only_supplied_portfolio(self):
        ctx=compact(self.feed,self.demo,"AAPL","Analizá AAPL")
        self.assertEqual({v["Ticker"] for v in ctx["top_positions"]},{"AAPL","SPY"})
        self.assertEqual(ctx["selected_ticker"]["Valor USD"],100.0)
        self.assertEqual(ctx["mentioned_ticker_details"]["AAPL"]["accounts"],["FICTICIA-1"])
        self.assertNotIn("PMS Bersoch",str(ctx))
    def test_context_does_not_invent_missing_holdings(self):
        ctx=compact(self.feed,self.demo,"TSLA","Compará TSLA con AAPL")
        self.assertNotIn("TSLA",ctx["mentioned_ticker_details"])
        self.assertIn("AAPL",ctx["mentioned_ticker_details"])
    def test_technical_snapshot_excludes_other_symbol(self):
        snapshot={"symbol":"MSFT","as_of":"2026-10-26"}
        self.assertFalse(eligible_technical_snapshot(snapshot,"AAPL",["AAPL"]))
        self.assertTrue(eligible_technical_snapshot({"symbol":"AAPL","as_of":"2026-10-26"},"AAPL",["AAPL"]))
    def test_technical_indicators_reject_nan(self):
        snapshot={"close_adjusted":100,"ema21":98,"ema50":95,"ema200":90,"rsi14":float("nan")}
        self.assertEqual(describe_technical_snapshot(snapshot)["quality"],"INDICADORES_INVALIDOS")
if __name__=="__main__":unittest.main()
