# Campus Customs MCP Server

This FastMCP server provides read-only retail operations tools. Every factual value comes from `data/campus_customs_new.db`; the original `data/campus_customs.db` is never modified. Quantities such as a stock shortfall are calculated from database values and the request arguments.

## Tools

### `retrieve_ticket_operations_context(ticket_id)`
Returns a `ticket` object plus `linked_records` containing any matching lease, invoice, and vendor rows. It supports tickets 101, 102, and 103 without inventing links.

### `inspect_product_stock_and_pricing(sku, size, requested_qty=1)`
Returns the request, the matching `inventory` row, the matching `pricing` row, and an `availability` object with database quantity and a calculated shortfall.

### `summarize_cash_rent_and_vendor_obligations()`
Returns the complete `cash_accounts`, `leases`, `vendor_invoices` joined to vendor details, and `payments` rows needed for approval decisions.

## Complete catalog and policy

The server currently exposes `retrieve_ticket_operations_context`, `inspect_product_stock_and_pricing`, and `summarize_cash_rent_and_vendor_obligations`. Every returned shop fact comes from `data/campus_customs_new.db`. The agent team records append-only audit entries in `output/audit_trail.json`. Money requires human approval; tools must not create negative balances; customer and vendor communications remain drafts; delegation and token use are bounded; and the original database remains untouched.
