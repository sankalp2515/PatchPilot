# PatchPilot business plan

Created and read back through the authenticated **cfo.ai MCP**, in the separate `PatchPilot launch hypotheses` scenario. [Open the saved economics table](https://app.cfo.ai/s/p_AQKFqAYkZDJiMDlhNTEtZTAzNS00NmFiLTkwNDktY2I1MDc4NGZiMjZiJGZiMDNiNGFkLTY1NjgtNDZjZS1iMzlhLWMzNjBkNzc3ODgxZg). The [saved-model receipt](evidence/cfo-model.json) retains formulas and returned values: 45 selected cells, 44 nonempty cells, zero formula errors. Growth runway is intentionally null because that case has no positive burn.

## Buyer and problem

SaaS integration engineers maintain adapters around changing APIs. A plausible repair can pass five known cases while mishandling expanded payment objects. PatchPilot provides a more inspectable research-and-review workflow: official version evidence, literal quotations, protected acceptance cases, independent counterexamples and a portable diff/report. No paying customers, validated demand or measured time savings are claimed.

## Offering and route to market

The shipped product is a free local prototype with bring-your-own keys. **$19/month individual** and **$79/month team** are pricing experiments, not implemented paid plans. Base average monthly price of $34 equals a hypothetical mix of 30 individual and 10 team buyers. Other average prices represent different mix/discount assumptions.

Reach integration consultants and SaaS teams through developer communities and public migration walkthroughs. Interview ten engineers, observe existing review work, offer a small reviewed pilot, and validate retention and conversion before charging. A hosted team offering requires additional authentication, tenant isolation and operations.

## Editable cfo.ai cases

All amounts are **USD assumptions**. Customer counts, repair rates, provider/compute cost, review costs, operating expenses and opening cash are illustrative hypotheses, not bank balances, revenue, invoices or an independent accuracy study.

| Monthly quantity | Conservative | Base | Growth |
|---|---:|---:|---:|
| Paying customers | 10 | 40 | 100 |
| Average price | $25 | $34 | $40 |
| Investigations/customer | 30 | 20 | 15 |
| Useful repair rate | 35% | 60% | 75% |
| Search/inference/compute per investigation | $0.12 | $0.08 | $0.08 |
| Review cost per useful repair | $2.00 | $1.00 | $0.50 |
| Revenue | $250 | $1,360 | $4,000 |
| Direct costs including review | $246 | $544 | $682.50 |
| Gross profit | $4 | $816 | $3,317.50 |
| Gross margin | 1.6% | 60% | 82.94% |
| Operating expense | $2,000 | $2,000 | $2,000 |
| Net burn | $1,996 | $1,184 | $0 |
| Hypothetical opening cash | $10,000 | $10,000 | $10,000 |
| Static runway | 5.01 months | 8.45 months | No positive burn |

The conservative case exposes review economics. Base reviewers cost $480 versus $64 in assumed search/inference/compute, so lowering model price alone does little. Growth is optimistic and excludes acquisition expansion. Add acquisition, support, churn, taxes and fees before treating this as a funded plan.

## Formula logic

Revenue = customers × price. Investigations = customers × volume. Direct costs = investigations × (provider/compute cost + useful repair rate × review cost). Gross margin = gross profit / revenue. Net burn = max(operating expense − gross profit, 0). Static runway = cash / positive burn; null otherwise. cfo.ai retains these dependencies. Edit an input to explore consequences.

Cost per useful repair includes failed investigations: provider/compute cost divided by useful repair rate, plus review cost (base $1.13 under these assumptions). Absent billing measurements remain absent. [Latest live usage](live-verification.json) records provider calls, tokens and runtime, not actual charges.

## Validation gates

Measure reviewed correctness, abstention, counterexample failures, reviewer minutes, repeat use and pilot conversion. Replace assumed cost with actual account rates and billable usage. Expand held-out migrations beyond Stripe. Keep results scoped and human-reviewed; do not auto-apply patches to payment systems.
