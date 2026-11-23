"""FORGE conservative spending guard and observed usage ledger.

Estimates are informative, not billing guarantees. External provider-side budgets
are required for a strict account-level ceiling.
"""
from dataclasses import dataclass, field
import math

# Standard short-context token prices in USD per million, checked 2026-11-16.
PRICES = {
    "gpt-6-astra": (10.0, 50.0),
    "gpt-6.1-sol": (2.0, 10.0),
    "gpt-6.1-terra": (1.0, 5.0),
    "gpt-6-luna": (0.10, 0.50),
}
# A deliberately conservative configurable estimate for each standard web-search call.
WEB_SEARCH_ESTIMATE = 0.02
SEARCH_PRICE_FLOOR = 0.01

@dataclass
class UsageLedger:
    budget: float = 0.75
    total: float = 0.0
    records: list = field(default_factory=list)

    def quote(self, model, input_chars, output_cap, search=False):
        if model not in PRICES:
            raise ValueError(f"No price configured for {model}; select a supported model.")
        if self.budget <= 0:
            raise ValueError("Run budget must be greater than zero.")
        # Rough upper-bound estimate on request tokens, *not* actual provider tokenization.
        estimated_input = math.ceil(max(0, input_chars) / 2) + 2500
        ip, op = PRICES[model]
        return (estimated_input * ip + output_cap * op) / 1_000_000 + (
            WEB_SEARCH_ESTIMATE if search else 0
        )

    def preflight(self, model, input_chars, output_cap, search=False):
        estimate = self.quote(model, input_chars, output_cap, search)
        if self.total + estimate > self.budget:
            raise ValueError(
                f"Run budget safeguard stopped the call: estimated upper envelope "
                f"${self.total + estimate:.3f} exceeds ${self.budget:.2f}. "
                f"Raise the limit or select a cheaper model."
            )
        return estimate

    def record(self, model, agent, response, search=False, reservation=None):
        usage = getattr(response, "usage", None)
        input_t = int(getattr(usage, "input_tokens", 0) or 0)
        output_t = int(getattr(usage, "output_tokens", 0) or 0)
        details = getattr(usage, "input_tokens_details", None)
        cached_t = int(getattr(details, "cached_tokens", 0) or 0)
        ip, op = PRICES[model]
        # Cached input rates: Astra $1, Sol $0.10, Terra $0.05, Luna $0.01
        cache_price = {"gpt-6-astra":1., "gpt-6.1-sol":.10,
                       "gpt-6.1-terra":.05, "gpt-6-luna":.01}[model]
        token_cost = ((input_t - cached_t)*ip + cached_t*cache_price + output_t*op) / 1_000_000
        raw = response.model_dump(mode="json")
        searches = sum(1 for x in raw.get("output", []) if x.get("type") == "web_search_call")
        # Actual tool costs can include additional billed content. This is an estimate.
        tool_estimate = searches * WEB_SEARCH_ESTIMATE
        amount = token_cost + tool_estimate
        if not usage:
            # Do not falsely mark unreported usage as zero.
            amount = float(reservation or 0)
        self.total += amount
        item = dict(agent=agent, model=model, input_tokens=input_t,
                    output_tokens=output_t, cached_input_tokens=cached_t,
                    web_search_calls=searches, estimated_usd=round(amount, 6),
                    reported_usage=bool(usage))
        self.records.append(item)
        return item
