# PatchPilot Business Model Inputs

This is a preparation worksheet for cfo.ai, not a completed cfo.ai plan or validated demand. The proposed buyer is an integration engineer or a small SaaS team with recurring documented API migration incidents. The purchase hypothesis is reduced investigation and review time per correctly verified repair.

## Measured usage

The initial successful live smoke used two search queries, one model proposal and 2,229 reported tokens, completing in 5.91 seconds. Subsequent final verification may have different counts; the latest authoritative summary is `live-verification.json`, and complete history is in the local run exports. Search/model counters initially measured logical operations; transport retries must be included when calculating billed usage. No provider price has been assumed to be verified from account billing.

## Pricing experiments to validate

| Hypothesis | Proposed experiment |
| --- | --- |
| Individual plan | Test $19/month with a small included investigation allowance. |
| Team plan | Test $79/month for shared review artifacts and a larger allowance. |
| Usage overage | Charge per additional investigation only after cost and value are established. |
| Primary value | Ask engineers to compare review minutes and incident resolution time with their existing workflow. |

These are illustrative test prices, not actual revenue, traction or commitments.

## Cost model

For each investigation: search requests x account search price + input/output tokens x selected model rates + computation/storage + observability + allocated reviewer/support cost. Use current actual account rates. Total-token reporting alone cannot distinguish input/output prices; instrument provider usage before publishing a margin forecast.

Track the verified repair rate, abstention rate, false verified verdicts, manual reviewer minutes, repeated incidents and monthly investigations per customer. Cost per useful repair = total investigation cost / correctly verified repair count. Include failed and abstaining runs in total cost.

## Scenarios to build in cfo.ai

Conservative: few paying teams, higher review costs and low successful repair rate. Base: modest paid adoption and measured incident volume. Growth: more customers plus proportionate inference, search and support expense. Revenue = paying customers x average realized monthly price. Gross margin = (revenue - direct costs) / revenue. Runway = available cash / positive monthly net burn. Treat every customer, churn and acquisition assumption as a hypothesis.

Runway needs real starting cash and monthly operating expense inputs from the user. Do not invent them or claim an account-backed cfo.ai export before one exists.
