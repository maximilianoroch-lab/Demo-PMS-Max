import unittest
from demo_independence import check_source_independence, check_synthetic_inventory, assert_ready_for_public_demo, REAL_SHEET_ID, DEMO_SHEET_ID
class IndependenceTests(unittest.TestCase):
 def test_synthetic_inventory(self):
  self.assertTrue(check_synthetic_inventory())
 def test_real_sheet_rejected(self):
  with self.assertRaises(ValueError): check_source_independence(REAL_SHEET_ID,"independent",True)
 def test_legacy_not_certified(self):
  self.assertFalse(check_source_independence(DEMO_SHEET_ID,"demo_legacy_scaled",False))
 def test_copy_not_enough(self):
  self.assertFalse(check_source_independence(DEMO_SHEET_ID,"independent",False))
 def test_cannot_claim_ready(self):
  with self.assertRaises(ValueError): assert_ready_for_public_demo(DEMO_SHEET_ID,"demo_legacy_scaled")
if __name__=="__main__": unittest.main()
