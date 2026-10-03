#!/usr/bin/env python3
"""Tests for autofin. Run: python3 -m unittest test_autofin (from scripts/).

Published references:
  * Edmunds, "How to Calculate Your Own Car Lease Payment": MSRP 45,000, 57% residual,
    MF 0.00125, price 43,000, fees 1,200, 2,000 down, 500 rebate, 36 months.
    Adjusted cap 41,700; rent charge 84.19.
  * Car Finance Tools, "Lease Money Factor Calculator": adj cap 66,100, residual 39,650,
    39 months, 869 pre-tax; MF ~0.00180, APR ~4.32%.
  * Standard amortization: 30,000 at 6% for 60 months = 579.98/month.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import autofin as A  # noqa: E402


EDMUNDS = {
    "msrp": 45000, "selling_price": 43000, "residual_percent": 57, "money_factor": 0.00125,
    "term_months": 36, "cash_down": 2000, "rebates": 500, "other_capitalized_fees": 1200,
    "acquisition_fee": 0,
}


class Lease(unittest.TestCase):
    def test_edmunds_forward(self):
        r = A.run("lease", EDMUNDS)
        self.assertEqual(r["adjusted_cap_cost"], 41700.00)
        self.assertEqual(r["residual_value"], 25650.00)
        self.assertEqual(r["rent_charge_per_month"], 84.19)
        self.assertEqual(r["depreciation_per_month"], 445.83)
        self.assertEqual(r["base_payment"], 530.02)
        self.assertEqual(r["apr_mf_x_2400"], 3.0)

    def test_carfinancetools_reverse_mf(self):
        r = A.run("lease", {"selling_price": 66100, "residual_value": 39650, "term_months": 39,
                            "monthly_payment": 869, "payment_includes_tax": False})
        self.assertEqual(r["solved_for"], "money_factor")
        self.assertAlmostEqual(r["money_factor"], 0.00180, places=5)
        self.assertAlmostEqual(r["apr_mf_x_2400"], 4.32, places=1)

    def test_round_trip_monthly_tax(self):
        fwd = dict(EDMUNDS, tax_rate=8.25, tax_method="monthly", acquisition_fee=695,
                   doc_fee=150, upfront_fees=400)
        out = A.run("lease", fwd)
        rev = dict(fwd)
        rev.pop("money_factor")
        rev["monthly_payment"] = out["monthly_payment"]
        back = A.run("lease", rev)
        self.assertAlmostEqual(back["money_factor"], 0.00125, delta=back["money_factor_precision"])

    def test_round_trip_texas_capitalized_tax(self):
        fwd = dict(EDMUNDS, tax_rate=6.25, tax_method="upfront_on_price", tax_capitalized=True,
                   acquisition_fee=650)
        out = A.run("lease", fwd)
        self.assertEqual(out["monthly_tax"], 0.0)
        self.assertEqual(out["tax_capitalized"], 2687.50)       # 43,000 x 6.25%
        rev = dict(fwd)
        rev.pop("money_factor")
        rev["monthly_payment"] = out["monthly_payment"]
        back = A.run("lease", rev)
        self.assertAlmostEqual(back["money_factor"], 0.00125, delta=back["money_factor_precision"])

    def test_reverse_selling_price_and_residual(self):
        out = A.run("lease", EDMUNDS)
        p = dict(EDMUNDS)
        p.pop("selling_price")
        p["monthly_payment"] = out["monthly_payment"]
        self.assertAlmostEqual(A.run("lease", p)["selling_price"], 43000, delta=1.0)
        p = dict(EDMUNDS)
        p.pop("residual_percent")
        p["monthly_payment"] = out["monthly_payment"]
        self.assertAlmostEqual(A.run("lease", p)["residual_value"], 25650, delta=2.0)

    def test_implicit_rate_close_to_mf_rule(self):
        r = A.run("lease", EDMUNDS)
        self.assertLess(abs(r["apr_implicit"] - 3.0), 0.25)

    def test_unknown_key_rejected(self):
        with self.assertRaises(A.InputError):
            A.run("lease", dict(EDMUNDS, moneyfactor=0.001))

    def test_quote_gap_reported(self):
        r = A.run("lease", dict(EDMUNDS, monthly_payment=560, payment_includes_tax=False))
        self.assertEqual(r["quoted_payment_gap"], 29.98)
        self.assertTrue(r["warnings"])


class Loan(unittest.TestCase):
    def test_amortization(self):
        r = A.run("loan", {"selling_price": 30000, "apr": 6, "term_months": 60})
        self.assertEqual(r["monthly_payment"], 579.98)

    def test_reverse_apr(self):
        r = A.run("loan", {"selling_price": 30000, "monthly_payment": 579.98, "term_months": 60})
        self.assertAlmostEqual(r["apr"], 6.0, places=2)

    def test_tax_with_trade_credit(self):
        r = A.run("loan", {"selling_price": 40000, "apr": 5, "term_months": 60, "tax_rate": 6.25,
                           "trade_value": 10000, "trade_payoff": 4000})
        self.assertEqual(r["sales_tax"], 1875.00)               # (40,000 - 10,000) x 6.25%
        self.assertEqual(r["amount_financed"], 35875.00)

    def test_cash(self):
        r = A.run("loan", {"selling_price": 40000, "term_months": 0, "tax_rate": 6.25, "doc_fee": 150})
        self.assertEqual(r["total_cost"], 42650.00)


class Compare(unittest.TestCase):
    def setUp(self):
        self.lease = dict(EDMUNDS, tax_rate=6.25, tax_method="upfront_on_price",
                          tax_capitalized=True, acquisition_fee=650, disposition_fee=395)
        self.buy = {"selling_price": 43000, "rebates": 500, "msrp": 45000, "apr": 5.9,
                    "term_months": 60, "cash_down": 2000, "tax_rate": 6.25, "doc_fee": 150}

    def test_return_identity(self):
        c = A.run("compare", {"lease": self.lease, "buy": self.buy, "resale_value_at_horizon": 26000})
        cmp = c["comparison"]
        self.assertAlmostEqual(cmp["buy_minus_lease"], cmp["buy_net_cost"] - cmp["lease_net_cost"], places=1)
        # At the break-even resale the difference is zero.
        c2 = A.run("compare", {"lease": self.lease, "buy": self.buy,
                               "resale_value_at_horizon": cmp["break_even_resale"]})
        self.assertAlmostEqual(c2["comparison"]["buy_minus_lease"], 0.0, delta=0.02)

    def test_flows_sum_to_totals(self):
        c = A.run("compare", {"lease": self.lease, "buy": self.buy, "resale_percent_of_msrp": 55,
                              "discount_rate": 4})
        self.assertAlmostEqual(sum(c["cash_flows"]["lease"].values()), c["comparison"]["lease_net_cost"], delta=0.5)
        self.assertAlmostEqual(sum(c["cash_flows"]["buy"].values()), c["comparison"]["buy_net_cost"], delta=0.5)
        self.assertIn("lease_present_cost", c["comparison"])

    def test_buyout_horizon(self):
        c = A.run("compare", {"lease": self.lease, "buy": self.buy, "lease_end": "buyout",
                              "horizon_months": 72, "resale_value_at_horizon": 18000})
        self.assertEqual(c["comparison"]["horizon_months"], 72)
        self.assertEqual(c["comparison"]["loan_balance_at_horizon"], 0.0)

    def test_horizon_mismatch_rejected(self):
        with self.assertRaises(A.InputError):
            A.run("compare", {"lease": self.lease, "buy": self.buy, "horizon_months": 60})

    def test_deterministic(self):
        p = {"lease": self.lease, "buy": self.buy, "resale_value_at_horizon": 26000}
        self.assertEqual(A.run("compare", p), A.run("compare", p))


if __name__ == "__main__":
    unittest.main()
