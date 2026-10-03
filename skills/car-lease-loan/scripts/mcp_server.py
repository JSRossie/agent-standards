#!/usr/bin/env python3
"""Minimal stdio MCP server exposing autofin as tools. Standard library only.

Tools: lease_calc, loan_calc, lease_vs_buy, mf_apr_convert. Each takes the same JSON
object the CLI takes (see SKILL.md) and returns the CLI's JSON output. No network, no
filesystem writes, no state between calls.

Register in a Hermes profile:
    mcp_servers:
      car-finance:
        command: /usr/bin/python3
        args: [~/Local/agent-standards/skills/car-lease-loan/scripts/mcp_server.py]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autofin  # noqa: E402

PROTOCOL = "2025-06-18"
OBJ = {"type": "object", "additionalProperties": True}

TOOLS = [
    ("lease_calc", "lease",
     "Deterministic US car lease calculator. Forward (payment from money factor, price, "
     "residual) or reverse: omit exactly one of money_factor/apr, selling_price, residual "
     "(value or percent) and give monthly_payment to solve it. Returns money factor, MF x 2400, "
     "the true implicit APR, an all-in APR with lender fees, due at signing and total cost. "
     "Input keys are documented in the car-lease-loan skill; unknown keys are rejected."),
    ("loan_calc", "loan",
     "Deterministic auto loan or cash purchase. Payment from APR, or APR from payment. "
     "term_months 0 means cash. Handles sales tax with trade-in credit, fees, down payment."),
    ("lease_vs_buy", "compare",
     "Lease versus buy over one horizon as dated cash flows: {lease:{...}, buy:{...}, "
     "resale_value_at_horizon or resale_percent_of_msrp, horizon_months, lease_end "
     "'return'|'buyout', discount_rate}. Returns net cost of each, the difference, break-even "
     "resale, resale sensitivity, optional present-value costs, and the assumptions used."),
    ("mf_apr_convert", "convert",
     "Convert {money_factor} to APR (x 2400) or {apr} to money factor. The 2400 rule is an "
     "approximation; use lease_calc for the implicit rate."),
]
BY_NAME = {name: cmd for name, cmd, _ in TOOLS}


def reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(msg):
    method, id_ = msg.get("method"), msg.get("id")
    if id_ is None:
        return  # notification
    if method == "initialize":
        reply(id_, {"protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "car-finance", "version": autofin.__version__}})
    elif method == "ping":
        reply(id_, {})
    elif method == "tools/list":
        reply(id_, {"tools": [{"name": n, "description": d, "inputSchema": OBJ} for n, _, d in TOOLS]})
    elif method == "tools/call":
        params = msg.get("params", {})
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in BY_NAME:
            reply(id_, error={"code": -32602, "message": "unknown tool %r" % name})
            return
        try:
            out = autofin.run(BY_NAME[name], args)
            reply(id_, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}],
                        "structuredContent": out, "isError": False})
        except autofin.InputError as e:
            reply(id_, {"content": [{"type": "text", "text": "input error: %s" % e}], "isError": True})
    else:
        reply(id_, error={"code": -32601, "message": "method not found: %s" % method})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply(None, error={"code": -32700, "message": "parse error"})
            continue
        try:
            handle(msg)
        except Exception as e:  # never die on one bad call
            reply(msg.get("id"), error={"code": -32603, "message": str(e)})


if __name__ == "__main__":
    main()
