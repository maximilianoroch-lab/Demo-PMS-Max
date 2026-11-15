import unittest
import pandas as pd
from demo_price_history_gate import validate_price_history, rank_two_verified_dates, load_verified_price_history

def prices():
    return pd.DataFrame([
        dict(Fecha="2026-11-12",Ticker="AAPL",Precio="100",Moneda="ARS",
             Fuente="mercado",Referencia="https://example.org/2026-11-12",
             Fecha_fuente="2026-11-12",Origen_cartera="DEMO_V5_MERCADO_INDEPENDIENTE"),
        dict(Fecha="2026-11-13",Ticker="AAPL",Precio="110",Moneda="ARS",
             Fuente="mercado",Referencia="https://example.org/2026-11-13",
             Fecha_fuente="2026-11-13",Origen_cartera="DEMO_V5_MERCADO_INDEPENDIENTE")
    ])

class DemoPriceHistoryGateTests(unittest.TestCase):
    def test_two_valid_independent_prices(self):
        got=rank_two_verified_dates(prices())
        self.assertAlmostEqual(got.iloc[0]["Variacion_pct"],10)
        self.assertEqual(got.iloc[0]["Fecha_previa"],pd.Timestamp("2026-11-12"))
    def test_reject_copied_legacy_history(self):
        x=prices(); x["Origen_cartera"]="BERSOCH"
        with self.assertRaisesRegex(ValueError,"heredada"):
            validate_price_history(x)
    def test_reject_simulated_prices_as_market(self):
        x=prices();x["Origen_cartera"]="DEMO_SCALED"
        with self.assertRaises(ValueError):validate_price_history(x)
    def test_reject_missing_provenance(self):
        x=prices().drop(columns=["Referencia"])
        with self.assertRaisesRegex(ValueError,"columnas"):
            validate_price_history(x)
    def test_reject_mismatched_source_date(self):
        x=prices();x.loc[0,"Fecha_fuente"]="2026-11-11"
        with self.assertRaisesRegex(ValueError,"no coinciden"):
            validate_price_history(x)
    def test_reject_unrecognized_ticker(self):
        with self.assertRaisesRegex(ValueError,"ajenos"):
            validate_price_history(prices(),{"MSFT"})
    def test_reject_duplicate_rows(self):
        x=pd.concat([prices(),prices().iloc[[0]]],ignore_index=True)
        with self.assertRaisesRegex(ValueError,"duplicadas"):
            validate_price_history(x)
    def test_reject_nonpositive_prices(self):
        x=prices();x.loc[0,"Precio"]="0"
        with self.assertRaisesRegex(ValueError,"inválido"):
            validate_price_history(x)
    def test_reject_single_day(self):
        with self.assertRaisesRegex(ValueError,"dos fechas"):
            rank_two_verified_dates(prices().iloc[[0]])
    def test_no_history_is_blocked(self):
        with self.assertRaisesRegex(ValueError,"No existe"):
            load_verified_price_history("/path/that/does/not/exist/independent_demo_prices.csv")
    def test_no_cross_currency_comparison(self):
        x=prices();x.loc[0,"Moneda"]="USD"
        with self.assertRaisesRegex(ValueError,"comparables"):
            rank_two_verified_dates(x)

if __name__=="__main__": unittest.main()
