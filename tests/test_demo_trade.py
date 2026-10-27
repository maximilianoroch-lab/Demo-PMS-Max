import unittest
from demo_trade import simulate_demo_trade
class Trades(unittest.TestCase):
 def setUp(self):self.h={"AAPL":1000,"SPY":2000,"CASH":500}
 def case(self,op,amount,mode,source=None,cash=0):
  return simulate_demo_trade(self.h,"AAPL",op,amount,mode,source,cash)
 def test_cash_funded(self):
  r=self.case("Comprar",250,"CASH")
  self.assertEqual(r["total_after"],3500)
  self.assertEqual(r["cash_after"],250)
  self.assertEqual(r["value_after"],1250)
 def test_external_contribution(self):
  r=self.case("Comprar",250,"Aporte externo")
  self.assertEqual(r["total_after"],3750)
  self.assertEqual(r["cash_after"],500)
 def test_sell_to_cash(self):
  r=self.case("Vender",200,"CASH")
  self.assertEqual(r["total_after"],3500)
  self.assertEqual(r["cash_after"],700)
 def test_external_withdrawal(self):
  r=self.case("Vender",200,"Retiro externo")
  self.assertEqual(r["total_after"],3300)
  self.assertEqual(r["cash_after"],500)
 def test_sell_another_asset(self):
  r=self.case("Comprar",300,"Venta de otro activo","SPY")
  self.assertEqual(r["total_after"],3500)
  self.assertEqual(r["source_after"],1700)
 def test_blend(self):
  r=self.case("Comprar",300,"CASH + venta de activo","SPY",100)
  self.assertEqual(r["cash_after"],400)
  self.assertEqual(r["source_after"],1800)
 def test_reject_insufficient_cash(self):
  self.assertIn("error",self.case("Comprar",600,"CASH"))
 def test_reject_source_overdraft(self):
  self.assertIn("error",self.case("Comprar",2400,"Venta de otro activo","SPY"))
 def test_reject_oversell(self):
  self.assertIn("error",self.case("Vender",1200,"CASH"))
 def test_reject_negative_holdings(self):
  holdings={"AAPL":1000,"SPY":-50,"CASH":500}
  self.assertIn("error",simulate_demo_trade(holdings,"AAPL","Comprar",100,"CASH"))
 def test_reject_nan_amount(self):
  self.assertIn("error",self.case("Comprar",float("nan"),"CASH"))
 def test_reject_negative_cash_contribution(self):
  self.assertIn("error",self.case("Comprar",200,"CASH + venta de activo","SPY",-10))
 def test_zero_nav_rejected_without_division_error(self):
  self.assertIn("error",simulate_demo_trade({"AAPL":0,"CASH":0},"AAPL","Comprar",10,"Aporte externo"))
 def test_no_tolerance_allows_negative_cash(self):
  self.assertIn("error",simulate_demo_trade({"AAPL":10,"CASH":1},"AAPL","Comprar",1.004,"CASH"))
 def test_no_tolerance_allows_overselling(self):
  self.assertIn("error",simulate_demo_trade({"AAPL":10,"CASH":1},"AAPL","Vender",10.004,"CASH"))
 def test_rejects_malformed_numeric_input(self):
  self.assertIn("error",self.case("Comprar","abc","CASH"))
 def test_rejects_overflowed_final_position(self):
  holdings={"AAPL":1e308,"CASH":1e308}
  self.assertIn("error",simulate_demo_trade(holdings,"AAPL","Comprar",1e308,"Aporte externo"))
 def test_no_mutation(self):
  self.case("Comprar",100,"CASH")
  self.assertEqual(self.h,{"AAPL":1000,"SPY":2000,"CASH":500})
if __name__=="__main__": unittest.main()
