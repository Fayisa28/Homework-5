# Campus Customs Multi-Agent Operations

Campus Customs Multi-Agent Operations is the agentic team that runs the shop. Open tickets land on a board — customer orders, rent, unpaid bills, discount requests, whatever the shop has to handle. The system will include an MCP server, a FastAPI backend with a multi-agent team, and a React dashboard so a human can watch agents and approve requests.

## Agents

- Boss — reads each ticket, decides who should work on it, and makes final calls.
- Inventory — checks stock by SKU and size, spots shortfalls, and determines which vendor can restock.
- Accounting — watches cash and invoices, checks margins, and prepares payments or purchase orders for human approval.
- Facilities — handles the shop space side, including leases and rent.
- Customer Service — drafts customer messages.

## Data

Use `data/campus_customs.db` as the original database. Copy it to `data/campus_customs_new.db` and point the MCP server and backend at the working copy. Keep the original untouched so it can be used to reset the work.

Tables include `desk`, `tickets`, `inventory`, `pricing`, `vendors`, `leases`, `cash_accounts`, `payments`, and `invoices`.

## Rules

- Use `desk.date_today` as the shop's current date when determining overdue items.
- Vendor lead times come from the `vendors` table.
- Vendors will not ship new product while they have an open unpaid invoice.
- Human approval is required for all payments; update the relevant table after approval.
- The pay tool must refuse payments when cash is insufficient; balances cannot go negative.
- Cash only leaves the shop in this homework; no revenue is modeled.
- Reset the working database before a full ticket run.
- Do not email customers or call real vendors; keep drafts on the board.
- Use `PORTKEY_API_KEY` for AI calls and only `gpt-6-luna` through Portkey.
