import unittest
import pandas as pd
from demo_independent_model import parse_demo_numbers

class DemoLocaleTests(unittest.TestCase):
    def test_decimal_comma(self):
        out=parse_demo_numbers(pd.Series(["12,82195918","0,21204394","100"]))
        self.assertAlmostEqual(out.iloc[0],12.82195918)
        self.assertAlmostEqual(out.iloc[1],0.21204394)
        self.assertEqual(out.iloc[2],100)
    def test_invalid_number_rejected(self):
        with self.assertRaises(ValueError):
            parse_demo_numbers(pd.Series(["sin dato"]))

if __name__=="__main__": unittest.main()
