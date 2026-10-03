---
name: car-lease-loan
description: Use when a car lease, auto loan, or lease-versus-buy question needs numbers. Runs a deterministic calculator; never does the math by hand.
---

# Car lease and loan math

Lease and loan figures come from `scripts/autofin.py` (standard library, Python 3.9+) or
the same code exposed as MCP tools by `scripts/mcp_server.py`. **Never compute a payment,
money factor, rate, or total in your head or in prose.** Language-model arithmetic on
compounding is unreliable; the script is exact and repeatable. Your job is to extract the
inputs faithfully, call the tool, and explain the output.

| Need | MCP tool | CLI |
|---|---|---|
| Lease payment, or reverse-solve money factor / price / residual | `lease_calc` | `autofin.py lease --json '{…}'` |
| Loan payment or APR; cash purchase | `loan_calc` | `autofin.py loan --json '{…}'` |
| Lease versus buy over a horizon | `lease_vs_buy` | `autofin.py compare --json '{…}'` |
| MF ↔ APR quick conversion | `mf_apr_convert` | `autofin.py convert --mf 0.00125` |

Add `--text` on the CLI for a readable table. Tests: `cd scripts && python3 -m unittest test_autofin`.

## Workflow

1. **Collect the quote as written.** Ask for the worksheet or contract numbers, not a
   summary. Each input below is either stated on the document, stated by the user, or
   marked as an assumption in your answer. Never invent a residual, money factor, or fee.
2. **Reconcile first.** Run `lease_calc` forward with everything known. If the dealer
   quoted a payment, pass it as `monthly_payment` too: a non-zero `quoted_payment_gap`
   means the quote does not reconcile, which is the first finding to report.
3. **Reverse-engineer the unknown.** Leave out exactly one of `money_factor`/`apr`,
   `selling_price`, or `residual_value`/`residual_percent`, and give `monthly_payment`.
   The tool infers what to solve (or set `solve_for`).
4. **Compare** with `lease_vs_buy` on the same car, same horizon, same taxes.
5. **Report** using the template below, with the assumptions the tool returned.

## Lease inputs (`lease_calc`)

Money in dollars, rates in percent, money factor as a decimal. Unknown keys are rejected.

| Key | Meaning | Default |
|---|---|---|
| `term_months` | Lease term | required |
| `msrp` | Needed for `residual_percent` and benchmarks | – |
| `selling_price` | Negotiated price (cap cost before fees) | required unless solving |
| `residual_value` or `residual_percent` | Residual in dollars, or % of MSRP | required unless solving |
| `money_factor` or `apr` | Rate; `apr` is converted ÷ 2400 | required unless solving |
| `monthly_payment` | Quoted payment (for reverse solves and reconciliation) | – |
| `payment_includes_tax` | Whether the quoted payment includes monthly tax | `true` |
| `acquisition_fee`, `acquisition_fee_capitalized` | Bank fee; rolled in by default | 0, `true` |
| `doc_fee`, `doc_fee_capitalized` | Dealer doc fee; paid at signing by default | 0, `false` |
| `other_capitalized_fees` | Anything else rolled into the cap cost | 0 |
| `upfront_fees` | Title, registration, other fees paid at signing | 0 |
| `cash_down`, `rebates` | Cap cost reductions | 0 |
| `trade_value`, `trade_payoff` | Trade-in; equity reduces cap cost | 0 |
| `tax_rate`, `tax_method` | See tax methods below | 0, `monthly` |
| `tax_capitalized` | Upfront tax rolled into the cap cost | `false` |
| `taxable_price` | Override the base for `upfront_on_price` | selling price |
| `tax_cap_reduction` | Cash down and rebates are taxed | `true` |
| `security_deposit` | Refundable deposit | 0 |
| `disposition_fee`, `purchase_option_fee` | End-of-lease fees | 0 |
| `miles_per_year_allowed`, `expected_miles_per_year`, `excess_mile_rate` | Mileage overage cost | – |

**Tax methods.** `monthly`: tax on each payment (most states). `upfront_on_price`: tax on
the full selling price at signing (Texas: confirm the current rule; dealers usually
capitalize it, so set `tax_capitalized: true`). `upfront_on_payments`: tax on the sum of
payments plus the down payment, at signing (e.g. NY, NJ). `none`. When the state is
unclear, ask, or run both and show the spread.

**Outputs to explain.**

- `money_factor`, plus `money_factor_precision`. A quoted payment is rounded to the cent,
  so a reverse-solved money factor is only known to about ± that figure. Do not report
  more digits than that.
- `apr_mf_x_2400`. The industry convention, and the number to compare against the lender's
  published buy rate. Any excess over the buy rate is markup.
- `apr_implicit`. The true interest rate implied by the cap cost, the payments in advance
  and the residual. This is the honest rate.
- `apr_all_in`. The rate after counting the acquisition fee, doc fee, other capitalized
  fees and the disposition fee as financing costs. This is the figure to set against a
  loan APR. Taxes are excluded from every rate.
- `due_at_signing`, `total_cost_if_returned` (all cash out, minus a returned deposit,
  plus overage and disposition), `buyout_at_term`.
- `warnings`: a gap between the quote and the math, a negative money factor (an incentive
  or fee is missing), or a residual outside 30 to 75% of MSRP.

## Loan inputs (`loan_calc`)

`selling_price` (required), `term_months` (0 = cash), `apr` **or** `monthly_payment`
(the other is solved), `cash_down`, `rebates`, `trade_value`, `trade_payoff`, `tax_rate`,
`taxable_price`, `trade_in_tax_credit` (default `true`; the trade value reduces taxable
price), `tax_financed` (default `true`), `doc_fee`, `upfront_fees`, `fees_financed`
(default `true`), `msrp`. Payments are in arrears. Outputs: amount financed, payment,
APR, total interest, total cost.

## Lease versus buy (`lease_vs_buy`)

```json
{"lease": {…lease inputs…}, "buy": {…loan inputs…},
 "horizon_months": 36, "lease_end": "return",
 "resale_value_at_horizon": 28600, "discount_rate": 4,
 "lease_extra_monthly": 0, "buy_extra_monthly": 0, "sensitivity_percent": 15}
```

- **Return** (default): the horizon equals the lease term. Lease cost = everything paid in,
  plus disposition and overage, minus a returned deposit. Buy cost = everything paid in,
  plus the loan balance still owed at the horizon, minus the car's resale value then.
- **Buyout**: `lease_end: "buyout"` with `horizon_months` ≥ term. The lease side pays the
  residual, the purchase-option fee and the buyout tax (`buyout_tax_rate` or `buyout_tax`;
  defaults to the lease tax rate, and that default is flagged), then sells at the horizon.
  Use this for "lease now and buy it out" against "buy now and keep."
- **Resale is the swing variable.** Give `resale_value_at_horizon` or
  `resale_percent_of_msrp` from a cited source (a KBB/Edmunds projection, or the lease
  residual as a proxy, which the tool assumes and flags when the horizon equals the term).
  Always report `break_even_resale`: buying wins if the car is worth more than that at the
  horizon. Show the `sensitivity_to_resale` rows.
- **Time value.** `discount_rate` (annual %, e.g. the user's savings yield) adds present
  value costs. Report the nominal and present-value results together when they disagree
  on the winner.
- **Like for like.** Same car, same price, same taxes and fees on both sides. Put costs
  that differ between the two options (gap insurance on the lease, extra maintenance after
  warranty on the buy) in `lease_extra_monthly` / `buy_extra_monthly`. Do not add costs
  both sides share (fuel, base insurance). The resale figure must reflect the miles the
  user will actually drive.

## Report template

```
Bottom line: <lease|buy> is cheaper by $X over N months (present value: $Y at d%).
Break-even resale: $B (P% of MSRP); buying wins if the car is worth more than that.

Lease: MF 0.00xxxx (± p) = x.xx% by the 2400 rule; true rate x.xx%; all-in x.xx% with fees.
  $pmt/mo, $D due at signing, $T total if returned.
Buy: $pmt/mo at x.xx% APR, $D at signing; $T net after selling at $R.

Quote check: <reconciles | gap of $g/mo; ask the dealer about it>
Assumptions: <from the tool, plus any you supplied, each with its source>
```

## Pitfalls

- **Rounding.** Dealer worksheets round the payment, and some round the rent charge and
  depreciation separately. A gap under $1 is rounding; a larger gap is a real difference.
- **First payment.** It is part of due at signing; the tool counts it once.
- **Leases with no money down.** Rolled-in fees and taxes raise the cap cost. Enter them as
  capitalized, not as cash.
- **Money factor markup.** Compare `apr_mf_x_2400` with the lender's published buy rate
  for the same tier, term and month before calling it a markup. Without that evidence,
  report the rate, not an accusation.
- **Multiple security deposits.** Enter the lowered money factor and the total deposit in
  `security_deposit`; the deposit comes back at the end.
- **Not covered:** one-pay leases, balloon loans, rent-to-own, non-US leases. Say so
  rather than forcing the inputs to fit.
- This is decision support, not financial or tax advice. Taxes vary by state and change;
  confirm the current rule.
