#!/usr/bin/env python3
"""autofin: deterministic US car lease and loan math, and lease-versus-buy comparison.

Standard library only; runs on Python 3.9+. Every function is pure: the same input
dict always yields the same output dict. Inputs are validated strictly (an unknown key
is an error, so a typo cannot silently become a default).

CLI:
    autofin.py lease   --json '{...}' | --file in.json   [--text]
    autofin.py loan    --json '{...}' | --file in.json   [--text]
    autofin.py compare --json '{...}' | --file in.json   [--text]
    autofin.py convert --mf 0.00125 | --apr 3.0

Conventions (see SKILL.md for the full input reference):
    * Money in dollars, rates in percent (6.25 means 6.25%), money factor as a decimal.
    * Lease payments are in advance (first payment at signing), as US closed-end leases are.
    * Loan payments are in arrears (first payment one month after signing).
    * Rates exclude taxes; total costs include them.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

__version__ = "1.0.0"


class InputError(ValueError):
    """Raised for missing, unknown, or inconsistent inputs."""


# --------------------------------------------------------------------------- helpers

def _bisect(f, lo, hi, tol=1e-13, maxit=400):
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if (flo < 0) == (fhi < 0):
        raise InputError("no solution in range [%g, %g]; check the inputs" % (lo, hi))
    for _ in range(maxit):
        mid = (lo + hi) / 2.0
        fm = f(mid)
        if fm == 0 or (hi - lo) / 2.0 < tol:
            return mid
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2.0


def _r2(x):
    return None if x is None else round(x + 0.0, 2)


def _check_keys(d, allowed, where):
    if not isinstance(d, dict):
        raise InputError("%s must be an object" % where)
    unknown = sorted(set(d) - set(allowed))
    if unknown:
        raise InputError("%s: unknown key(s) %s; allowed: %s" % (where, unknown, sorted(allowed)))


def _num(d, key, default=None, required=False, minimum=None):
    if key not in d or d[key] is None:
        if required:
            raise InputError("missing required input '%s'" % key)
        return default
    v = d[key]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise InputError("'%s' must be a number, got %r" % (key, v))
    v = float(v)
    if minimum is not None and v < minimum:
        raise InputError("'%s' must be >= %g, got %g" % (key, minimum, v))
    return v


def _bool(d, key, default):
    v = d.get(key, default)
    if not isinstance(v, bool):
        raise InputError("'%s' must be true or false, got %r" % (key, v))
    return v


def _pv_due(pmt, r, n):
    """Present value of n level payments in advance (t = 0 .. n-1)."""
    return sum(pmt * (1.0 + r) ** -k for k in range(n))


def mf_to_apr(mf):
    return mf * 2400.0


def apr_to_mf(apr):
    return apr / 2400.0


# --------------------------------------------------------------------------- lease

LEASE_KEYS = {
    "msrp", "selling_price", "term_months",
    "residual_value", "residual_percent",
    "money_factor", "apr", "monthly_payment", "payment_includes_tax",
    "acquisition_fee", "acquisition_fee_capitalized",
    "doc_fee", "doc_fee_capitalized",
    "other_capitalized_fees", "upfront_fees",
    "cash_down", "rebates", "trade_value", "trade_payoff",
    "tax_rate", "tax_method", "tax_capitalized", "taxable_price", "tax_cap_reduction",
    "security_deposit", "disposition_fee", "purchase_option_fee",
    "miles_per_year_allowed", "expected_miles_per_year", "excess_mile_rate",
    "solve_for", "label",
}
TAX_METHODS = ("monthly", "upfront_on_price", "upfront_on_payments", "none")
LEASE_SOLVE = ("payment", "money_factor", "selling_price", "residual_value")


def _lease_inputs(p):
    _check_keys(p, LEASE_KEYS, "lease")
    q = {}
    q["label"] = p.get("label", "lease")
    q["N"] = int(_num(p, "term_months", required=True, minimum=1))
    if q["N"] != _num(p, "term_months"):
        raise InputError("'term_months' must be a whole number")
    q["msrp"] = _num(p, "msrp", minimum=0)
    q["price"] = _num(p, "selling_price", minimum=0)
    rv, rp = _num(p, "residual_value", minimum=0), _num(p, "residual_percent", minimum=0)
    if rv is not None and rp is not None:
        raise InputError("give residual_value or residual_percent, not both")
    if rp is not None:
        if q["msrp"] is None:
            raise InputError("residual_percent needs msrp")
        rv = q["msrp"] * rp / 100.0
    q["R"] = rv
    mf, apr = _num(p, "money_factor"), _num(p, "apr")
    if mf is not None and apr is not None:
        raise InputError("give money_factor or apr, not both")
    q["mf"] = apr_to_mf(apr) if apr is not None else mf
    q["payment"] = _num(p, "monthly_payment", minimum=0)
    q["pay_incl_tax"] = _bool(p, "payment_includes_tax", True)
    q["acq"] = _num(p, "acquisition_fee", 0.0, minimum=0)
    q["acq_cap"] = _bool(p, "acquisition_fee_capitalized", True)
    q["doc"] = _num(p, "doc_fee", 0.0, minimum=0)
    q["doc_cap"] = _bool(p, "doc_fee_capitalized", False)
    q["other_cap"] = _num(p, "other_capitalized_fees", 0.0, minimum=0)
    q["upfront_fees"] = _num(p, "upfront_fees", 0.0, minimum=0)
    q["down"] = _num(p, "cash_down", 0.0, minimum=0)
    q["rebates"] = _num(p, "rebates", 0.0, minimum=0)
    q["trade_value"] = _num(p, "trade_value", 0.0, minimum=0)
    q["trade_payoff"] = _num(p, "trade_payoff", 0.0, minimum=0)
    q["tax_rate"] = _num(p, "tax_rate", 0.0, minimum=0) / 100.0
    q["tax_method"] = p.get("tax_method", "monthly" if q["tax_rate"] > 0 else "none")
    if q["tax_method"] not in TAX_METHODS:
        raise InputError("tax_method must be one of %s" % (TAX_METHODS,))
    q["tax_cap"] = _bool(p, "tax_capitalized", False)
    q["taxable_price"] = _num(p, "taxable_price", minimum=0)
    q["tax_cap_reduction"] = _bool(p, "tax_cap_reduction", True)
    q["deposit"] = _num(p, "security_deposit", 0.0, minimum=0)
    q["disp"] = _num(p, "disposition_fee", 0.0, minimum=0)
    q["pof"] = _num(p, "purchase_option_fee", 0.0, minimum=0)
    q["miles_allowed"] = _num(p, "miles_per_year_allowed", minimum=0)
    q["miles_expected"] = _num(p, "expected_miles_per_year", minimum=0)
    q["mile_rate"] = _num(p, "excess_mile_rate", 0.0, minimum=0)

    solve = p.get("solve_for")
    if solve is None:
        missing = [k for k, v in (("money_factor", q["mf"]), ("selling_price", q["price"]),
                                  ("residual_value", q["R"])) if v is None]
        if not missing:
            solve = "payment"
        elif len(missing) == 1 and q["payment"] is not None:
            solve = missing[0]
        else:
            raise InputError("cannot tell what to solve: missing %s%s" % (
                missing, "" if q["payment"] is not None else " and no monthly_payment"))
    if solve not in LEASE_SOLVE:
        raise InputError("solve_for must be one of %s" % (LEASE_SOLVE,))
    if solve != "payment" and q["payment"] is None:
        raise InputError("solving for %s needs monthly_payment" % solve)
    for k, name in (("mf", "money_factor"), ("price", "selling_price"), ("R", "residual_value")):
        if name != solve and q[k] is None:
            raise InputError("missing required input '%s' (or its alternative)" % name)
    q["solve"] = solve
    return q


def _lease_forward(q, mf=None, price=None, R=None):
    """Compute a lease given the money factor, price and residual. Pure."""
    mf = q["mf"] if mf is None else mf
    price = q["price"] if price is None else price
    R = q["R"] if R is None else R
    N, t = q["N"], q["tax_rate"]
    trade_equity = q["trade_value"] - q["trade_payoff"]
    cap_fees = (q["acq"] if q["acq_cap"] else 0.0) + (q["doc"] if q["doc_cap"] else 0.0) + q["other_cap"]
    reduction = q["down"] + q["rebates"] + trade_equity
    taxed_reduction = (q["down"] + q["rebates"]) if q["tax_cap_reduction"] else 0.0
    taxable_price = q["taxable_price"] if q["taxable_price"] is not None else price

    def upfront_tax(base):
        m = q["tax_method"]
        if m == "monthly":
            return taxed_reduction * t
        if m == "upfront_on_price":
            return taxable_price * t
        if m == "upfront_on_payments":
            return (base * N + taxed_reduction) * t
        return 0.0

    tax_in_cap = 0.0
    for _ in range(500):
        adj = price + cap_fees + tax_in_cap - reduction
        dep = (adj - R) / N
        rent = (adj + R) * mf
        base = dep + rent
        up = upfront_tax(base)
        new = up if q["tax_cap"] else 0.0
        if abs(new - tax_in_cap) < 1e-10:
            tax_in_cap = new
            break
        tax_in_cap = new
    else:
        raise InputError("capitalized tax did not converge")
    adj = price + cap_fees + tax_in_cap - reduction
    gross = price + cap_fees + tax_in_cap
    dep = (adj - R) / N
    rent = (adj + R) * mf
    base = dep + rent
    up = upfront_tax(base)
    monthly_tax = base * t if q["tax_method"] == "monthly" else 0.0
    payment = base + monthly_tax
    return {
        "money_factor": mf, "selling_price": price, "residual_value": R,
        "gross_cap_cost": gross, "cap_reduction": reduction, "adjusted_cap_cost": adj,
        "tax_capitalized_amount": tax_in_cap, "upfront_tax": up,
        "depreciation": dep, "rent_charge": rent, "base_payment": base,
        "monthly_tax": monthly_tax, "payment": payment,
    }


def _payment_target(q, f):
    """The figure the quoted monthly_payment should be compared to."""
    return f["payment"] if q["pay_incl_tax"] else f["base_payment"]


def _implicit_monthly_rate(adj, base, R, N):
    """Rate r with adj = sum_{k<N} base*(1+r)^-k + R*(1+r)^-N (payments in advance)."""
    return _bisect(lambda r: _pv_due(base, r, N) + R * (1.0 + r) ** -N - adj, -0.05, 0.25)


def lease(p):
    """Forward lease calculation, or reverse-solve one unknown from a known payment."""
    q = _lease_inputs(p)
    warnings, solved = [], q["solve"]
    if solved == "payment":
        f = _lease_forward(q)
    else:
        target = q["payment"]
        if solved == "money_factor":
            x = _bisect(lambda m: _payment_target(q, _lease_forward(q, mf=m)) - target, -0.01, 0.05)
            f = _lease_forward(q, mf=x)
        elif solved == "selling_price":
            x = _bisect(lambda s: _payment_target(q, _lease_forward(q, price=s)) - target, 0.0, 1e7)
            f = _lease_forward(q, price=x)
        else:
            x = _bisect(lambda v: target - _payment_target(q, _lease_forward(q, R=v)), 0.0, 1e7)
            f = _lease_forward(q, R=x)
    N, R, adj, base, mf = q["N"], f["residual_value"], f["adjusted_cap_cost"], f["base_payment"], f["money_factor"]

    # Precision: a quoted payment is rounded to the cent, so a reverse-solved figure is
    # only known to within the change a half-cent payment move would cause.
    precision = None
    if solved == "money_factor":
        scale = (1.0 + (q["tax_rate"] if q["tax_method"] == "monthly" and q["pay_incl_tax"] else 0.0))
        precision = 0.005 / scale / (adj + R)

    r = _implicit_monthly_rate(adj, base, R, N)
    apr_implicit = r * 1200.0

    # All-in rate: the lessee's financing cost against paying the net cash price,
    # counting lender fees (acquisition, doc, capitalized extras, disposition), excluding
    # government fees and taxes. Capitalized tax is treated as financed principal.
    trade_equity = q["trade_value"] - q["trade_payoff"]
    principal = (f["selling_price"] - q["rebates"] + f["tax_capitalized_amount"]
                 - q["down"] - trade_equity
                 - (0.0 if q["acq_cap"] else q["acq"]) - (0.0 if q["doc_cap"] else q["doc"]))
    end_cost = R + q["disp"]
    try:
        r_all = _bisect(lambda x: _pv_due(base, x, N) + end_cost * (1.0 + x) ** -N - principal, -0.05, 0.25)
        apr_all_in = r_all * 1200.0
    except InputError:
        apr_all_in = None
        warnings.append("all-in rate has no solution for these inputs")

    # Cash flows and totals (lease returned at end of term).
    noncap_fees = (0.0 if q["acq_cap"] else q["acq"]) + (0.0 if q["doc_cap"] else q["doc"]) + q["upfront_fees"]
    upfront_tax_paid = 0.0 if q["tax_cap"] else f["upfront_tax"]
    due_at_signing = f["payment"] + q["down"] + noncap_fees + upfront_tax_paid + q["deposit"]
    excess_miles = 0.0
    if q["miles_allowed"] is not None and q["miles_expected"] is not None:
        excess_miles = max(0.0, q["miles_expected"] - q["miles_allowed"]) * N / 12.0
    excess_charge = excess_miles * q["mile_rate"]
    total_payments = f["payment"] * N
    total_cost_return = (due_at_signing - f["payment"]) + total_payments + q["disp"] + excess_charge - q["deposit"]
    if trade_equity:
        total_cost_return += trade_equity  # equity given up counts as a cost
    rent_total = f["rent_charge"] * N

    apr_mf = mf_to_apr(mf)
    if abs(apr_mf - apr_implicit) > 0.25:
        warnings.append("MF x 2400 (%.2f%%) and the implicit rate (%.2f%%) differ by more than 0.25 pt"
                        % (apr_mf, apr_implicit))
    if mf < 0:
        warnings.append("money factor is negative: the quote does not reconcile, or a fee or "
                        "incentive is missing from the inputs")
    if q["msrp"] and R:
        rp = R / q["msrp"] * 100.0
        if rp > 75 or rp < 30:
            warnings.append("residual is %.1f%% of MSRP, outside the usual 30-75%% band; check it" % rp)

    out = {
        "label": q["label"],
        "solved_for": solved,
        "term_months": N,
        "money_factor": round(mf, 8),
        "money_factor_precision": None if precision is None else float("%.2g" % precision),
        "apr_mf_x_2400": round(apr_mf, 3),
        "apr_implicit": round(apr_implicit, 3),
        "apr_all_in": None if apr_all_in is None else round(apr_all_in, 3),
        "selling_price": _r2(f["selling_price"]),
        "residual_value": _r2(R),
        "residual_percent_of_msrp": round(R / q["msrp"] * 100.0, 2) if q["msrp"] else None,
        "gross_cap_cost": _r2(f["gross_cap_cost"]),
        "cap_cost_reduction": _r2(f["cap_reduction"]),
        "adjusted_cap_cost": _r2(adj),
        "depreciation_per_month": _r2(f["depreciation"]),
        "rent_charge_per_month": _r2(f["rent_charge"]),
        "base_payment": _r2(base),
        "monthly_tax": _r2(f["monthly_tax"]),
        "monthly_payment": _r2(f["payment"]),
        "upfront_tax": _r2(f["upfront_tax"]),
        "tax_capitalized": _r2(f["tax_capitalized_amount"]),
        "due_at_signing": _r2(due_at_signing),
        "total_of_payments": _r2(total_payments),
        "total_rent_charge": _r2(rent_total),
        "excess_miles": round(excess_miles, 0),
        "excess_mileage_charge": _r2(excess_charge),
        "disposition_fee": _r2(q["disp"]),
        "total_cost_if_returned": _r2(total_cost_return),
        "buyout_at_term": _r2(R + q["pof"]),
        "payment_to_msrp_percent": round(f["payment"] / q["msrp"] * 100.0, 3) if q["msrp"] else None,
        "warnings": warnings,
    }
    if q["payment"] is not None and solved == "payment":
        quoted = q["payment"]
        computed = f["payment"] if q["pay_incl_tax"] else base
        out["quoted_payment_gap"] = _r2(quoted - computed)
        if abs(quoted - computed) > 0.5:
            warnings.append("quoted payment differs from the computed payment by $%.2f; the quote "
                            "does not reconcile with these inputs" % (quoted - computed))
    out["_q"] = q
    out["_f"] = f
    return out


# --------------------------------------------------------------------------- loan

LOAN_KEYS = {
    "msrp", "selling_price", "term_months", "apr", "monthly_payment",
    "cash_down", "rebates", "trade_value", "trade_payoff",
    "tax_rate", "taxable_price", "trade_in_tax_credit", "tax_financed",
    "doc_fee", "upfront_fees", "fees_financed", "label",
}


def _loan_payment(A, r, n):
    if n == 0:
        return 0.0
    if r == 0:
        return A / n
    return A * r / (1.0 - (1.0 + r) ** -n)


def _loan_balance(A, r, pmt, k):
    if r == 0:
        return A - pmt * k
    g = (1.0 + r) ** k
    return A * g - pmt * (g - 1.0) / r


def loan(p):
    """Loan (or cash, with term_months 0) purchase. Solves APR when given a payment."""
    _check_keys(p, LOAN_KEYS, "loan")
    label = p.get("label", "buy")
    price = _num(p, "selling_price", required=True, minimum=0)
    msrp = _num(p, "msrp", minimum=0)
    n_f = _num(p, "term_months", 0.0, minimum=0)
    n = int(n_f)
    if n != n_f:
        raise InputError("'term_months' must be a whole number")
    apr, pay = _num(p, "apr"), _num(p, "monthly_payment", minimum=0)
    down = _num(p, "cash_down", 0.0, minimum=0)
    rebates = _num(p, "rebates", 0.0, minimum=0)
    tv, tp = _num(p, "trade_value", 0.0, minimum=0), _num(p, "trade_payoff", 0.0, minimum=0)
    t = _num(p, "tax_rate", 0.0, minimum=0) / 100.0
    taxable = _num(p, "taxable_price", minimum=0)
    credit = _bool(p, "trade_in_tax_credit", True)
    tax_fin = _bool(p, "tax_financed", True)
    doc = _num(p, "doc_fee", 0.0, minimum=0)
    gov = _num(p, "upfront_fees", 0.0, minimum=0)
    fees_fin = _bool(p, "fees_financed", True)

    base = price if taxable is None else taxable
    tax = max(0.0, base - (tv if credit else 0.0)) * t
    fees = doc + gov
    equity = tv - tp
    cash_price_net = price - rebates
    financed = cash_price_net - down - equity + (tax if tax_fin else 0.0) + (fees if fees_fin else 0.0)
    at_signing = down + (0.0 if tax_fin else tax) + (0.0 if fees_fin else fees)
    warnings = []

    if n == 0:
        # Cash purchase: everything is paid at signing.
        at_signing = cash_price_net - equity + tax + fees
        financed, r, pmt = 0.0, 0.0, 0.0
        apr_out = None
    else:
        if apr is None and pay is None:
            raise InputError("a financed loan needs apr or monthly_payment")
        if apr is not None and pay is not None:
            raise InputError("give apr or monthly_payment, not both")
        if financed <= 0:
            raise InputError("nothing is financed; use term_months 0 for a cash purchase")
        if apr is not None:
            r = apr / 1200.0
            pmt = _loan_payment(financed, r, n)
        else:
            pmt = pay
            if pmt * n < financed - 1e-9:
                raise InputError("payment x term is less than the amount financed (negative APR)")
            r = _bisect(lambda x: _loan_payment(financed, x, n) - pmt, 0.0, 0.25)
        apr_out = r * 1200.0

    total_payments = pmt * n
    interest = total_payments - financed if n else 0.0
    total_cost = at_signing + total_payments + (equity if n else 0.0)
    return {
        "label": label,
        "kind": "cash" if n == 0 else "loan",
        "term_months": n,
        "apr": None if apr_out is None else round(apr_out, 3),
        "selling_price": _r2(price),
        "sales_tax": _r2(tax),
        "fees": _r2(fees),
        "amount_financed": _r2(financed),
        "monthly_payment": _r2(pmt),
        "due_at_signing": _r2(at_signing),
        "total_of_payments": _r2(total_payments),
        "total_interest": _r2(interest),
        "total_cost": _r2(total_cost),
        "warnings": warnings,
        "_state": {"financed": financed, "r": r, "pmt": pmt, "n": n, "at_signing": at_signing,
                   "equity": equity, "msrp": msrp, "tax_rate": t},
    }


# --------------------------------------------------------------------------- compare

COMPARE_KEYS = {
    "lease", "buy", "horizon_months", "lease_end",
    "resale_value_at_horizon", "resale_percent_of_msrp",
    "discount_rate", "buyout_tax_rate", "buyout_tax",
    "lease_extra_monthly", "buy_extra_monthly", "sensitivity_percent",
}


def _npv(flows, d):
    """flows: dict month -> net outflow (positive = money out)."""
    return sum(v * (1.0 + d) ** -m for m, v in flows.items())


def compare(p):
    """Lease versus buy over one horizon, both as dated net cash flows."""
    _check_keys(p, COMPARE_KEYS, "compare")
    if "lease" not in p or "buy" not in p:
        raise InputError("compare needs both 'lease' and 'buy' objects")
    L = lease(p["lease"])
    B = loan(p["buy"])
    q, f, s = L["_q"], L["_f"], B["_state"]
    N = q["N"]
    end = p.get("lease_end", "return")
    if end not in ("return", "buyout"):
        raise InputError("lease_end must be 'return' or 'buyout'")
    H = int(_num(p, "horizon_months", N, minimum=1))
    if end == "return" and H != N:
        raise InputError("with lease_end 'return' the horizon must equal the lease term (%d); "
                         "use lease_end 'buyout' to compare over a longer horizon" % N)
    if end == "buyout" and H < N:
        raise InputError("horizon_months must be at least the lease term for a buyout")
    d = _num(p, "discount_rate", minimum=0)
    d_m = None if d is None else d / 1200.0
    lx = _num(p, "lease_extra_monthly", 0.0)
    bx = _num(p, "buy_extra_monthly", 0.0)
    msrp = q["msrp"] if q["msrp"] is not None else s["msrp"]

    assumptions = []
    rv, rpct = _num(p, "resale_value_at_horizon", minimum=0), _num(p, "resale_percent_of_msrp", minimum=0)
    if rv is not None and rpct is not None:
        raise InputError("give resale_value_at_horizon or resale_percent_of_msrp, not both")
    if rpct is not None:
        if not msrp:
            raise InputError("resale_percent_of_msrp needs msrp in lease or buy")
        rv = msrp * rpct / 100.0
    if rv is None:
        if H == N:
            rv = f["residual_value"]
            assumptions.append("resale at horizon not given: assumed equal to the lease residual "
                               "($%.2f). The residual is the lessor's forecast, not a market quote." % rv)
        else:
            raise InputError("resale_value_at_horizon (or resale_percent_of_msrp) is required "
                             "when the horizon differs from the lease term")

    # Lease cash flows (positive = money out).
    lf = {}

    def add(flows, m, v):
        flows[m] = flows.get(m, 0.0) + v

    pmt = f["payment"]
    add(lf, 0, L["due_at_signing"])
    for m in range(1, N):
        add(lf, m, pmt)
    trade_equity = q["trade_value"] - q["trade_payoff"]
    if trade_equity:
        add(lf, 0, trade_equity)
    if end == "return":
        add(lf, N, q["disp"] + L["excess_mileage_charge"] - q["deposit"])
    else:
        bt = _num(p, "buyout_tax")
        btr = _num(p, "buyout_tax_rate", minimum=0)
        if bt is None:
            rate = (btr if btr is not None else q["tax_rate"] * 100.0) / 100.0
            bt = f["residual_value"] * rate
            assumptions.append("buyout taxed at %.3f%% of the residual ($%.2f); confirm the "
                               "state's rule, which can differ for a lease buyout" % (rate * 100, bt))
        add(lf, N, f["residual_value"] + q["pof"] + bt - q["deposit"])
        add(lf, H, -rv)
    for m in range(0, H):
        if lx:
            add(lf, m, lx)

    # Buy cash flows.
    bf = {}
    add(bf, 0, s["at_signing"] + (s["equity"] if s["n"] else 0.0))
    for m in range(1, min(s["n"], H) + 1):
        add(bf, m, s["pmt"])
    balance = 0.0
    if s["n"] > H:
        balance = _loan_balance(s["financed"], s["r"], s["pmt"], H)
    add(bf, H, balance - rv)
    for m in range(0, H):
        if bx:
            add(bf, m, bx)

    lease_nom = sum(lf.values())
    buy_nom = sum(bf.values())
    res = {
        "horizon_months": H,
        "lease_end": end,
        "resale_value_at_horizon": _r2(rv),
        "loan_balance_at_horizon": _r2(balance),
        "lease_net_cost": _r2(lease_nom),
        "buy_net_cost": _r2(buy_nom),
        "buy_minus_lease": _r2(buy_nom - lease_nom),
        "cheaper": "lease" if lease_nom < buy_nom - 0.005 else ("buy" if buy_nom < lease_nom - 0.005 else "tie"),
        "lease_cost_per_month": _r2(lease_nom / H),
        "buy_cost_per_month": _r2(buy_nom / H),
    }
    # Break-even resale: the resale value at which the two options cost the same.
    # Buy cost falls one-for-one with resale (nominal); a buyout lease falls too.
    if end == "return":
        be = rv + (buy_nom - lease_nom)
    else:
        be = None  # both sides own the car at H; resale cancels except through timing
    res["break_even_resale"] = _r2(be)
    if be is not None and msrp:
        res["break_even_resale_percent_of_msrp"] = round(be / msrp * 100.0, 2)

    if d_m is not None:
        lp, bp = _npv(lf, d_m), _npv(bf, d_m)
        res["discount_rate"] = d
        res["lease_present_cost"] = _r2(lp)
        res["buy_present_cost"] = _r2(bp)
        res["buy_minus_lease_present"] = _r2(bp - lp)
        if end == "return":
            res["break_even_resale_present_basis"] = _r2(rv + (bp - lp) * (1.0 + d_m) ** H)

    sens = _num(p, "sensitivity_percent", 15.0, minimum=0)
    if sens and end == "return":
        rows = []
        for k in (-2, -1, 0, 1, 2):
            v = rv * (1.0 + k * sens / 200.0)
            rows.append({"resale": _r2(v), "buy_minus_lease": _r2(buy_nom - lease_nom - (v - rv))})
        res["sensitivity_to_resale"] = rows

    pub = {k: v for k, v in L.items() if not k.startswith("_")}
    pubB = {k: v for k, v in B.items() if not k.startswith("_")}
    if s["n"] and s["n"] < H:
        assumptions.append("the loan ends at month %d, before the horizon; no further car cost is "
                           "counted after payoff beyond the extras given" % s["n"])
    if lx or bx:
        assumptions.append("extra monthly costs included: lease $%.2f, buy $%.2f" % (lx, bx))
    assumptions.append("taxes, fees and trade equity are included in both totals; the financing "
                       "rates exclude taxes")
    assumptions.append("nominal totals ignore the time value of money unless discount_rate is given")
    return {"lease": pub, "buy": pubB, "comparison": res, "assumptions": assumptions,
            "cash_flows": {"lease": {str(k): _r2(v) for k, v in sorted(lf.items())},
                           "buy": {str(k): _r2(v) for k, v in sorted(bf.items())}}}


# --------------------------------------------------------------------------- public API

def run(command, payload):
    """Single entry point used by the CLI and the MCP server."""
    if command == "lease":
        out = lease(payload)
        return {k: v for k, v in out.items() if not k.startswith("_")}
    if command == "loan":
        out = loan(payload)
        return {k: v for k, v in out.items() if not k.startswith("_")}
    if command == "compare":
        return compare(payload)
    if command == "convert":
        _check_keys(payload, {"money_factor", "apr"}, "convert")
        if "money_factor" in payload:
            mf = _num(payload, "money_factor", required=True)
            return {"money_factor": mf, "apr_mf_x_2400": round(mf_to_apr(mf), 4)}
        apr = _num(payload, "apr", required=True)
        return {"apr": apr, "money_factor": round(apr_to_mf(apr), 7)}
    raise InputError("unknown command %r" % command)


def _text(command, out):
    lines = []

    def block(title, d):
        lines.append(title)
        for k, v in d.items():
            if k == "warnings":
                continue
            if v is None or isinstance(v, (list, dict)):
                continue
            lines.append("  %-34s %s" % (k, v))
        for w in d.get("warnings", []):
            lines.append("  WARNING: " + w)

    if command == "compare":
        block("LEASE (%s)" % out["lease"]["label"], out["lease"])
        block("BUY (%s)" % out["buy"]["label"], out["buy"])
        block("COMPARISON", out["comparison"])
        for row in out["comparison"].get("sensitivity_to_resale", []):
            lines.append("  resale %-12s buy_minus_lease %s" % (row["resale"], row["buy_minus_lease"]))
        for a in out["assumptions"]:
            lines.append("  ASSUMPTION: " + a)
    else:
        block(command.upper(), out)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="autofin", description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["lease", "loan", "compare", "convert"])
    ap.add_argument("--json", help="input as a JSON string")
    ap.add_argument("--file", help="input as a JSON file path")
    ap.add_argument("--mf", type=float, help="convert: money factor")
    ap.add_argument("--apr", type=float, help="convert: APR in percent")
    ap.add_argument("--text", action="store_true", help="human-readable output")
    a = ap.parse_args(argv)
    try:
        if a.command == "convert" and (a.mf is not None or a.apr is not None):
            payload = {"money_factor": a.mf} if a.mf is not None else {"apr": a.apr}
        elif a.json:
            payload = json.loads(a.json)
        elif a.file:
            with open(a.file) as fh:
                payload = json.load(fh)
        else:
            payload = json.load(sys.stdin)
        out = run(a.command, payload)
    except (InputError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2
    print(_text(a.command, out) if a.text else json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
