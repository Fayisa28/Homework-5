# Campus Customs Operations Harness

This manual documents the working database and the decisions the agent team must make when resolving tickets. The original `data/campus_customs.db` remains untouched; agents and tools use the resettable copy `data/campus_customs_new.db`.

## Operating date

### desk

| Field | Type | Operational use |
|---|---|---|
| `date_today` | TEXT NOT NULL | The shop’s operating date. Agents use it to determine whether rent and invoices are overdue. |
| `notes` | TEXT | Optional desk notes for the operations team. |

Current value: `2026-08-31`.

## Financial and facility tables

### cash_accounts

| Field | Type | Operational use |
|---|---|---|
| `name` | TEXT PRIMARY KEY | Account identifier, currently `checking`. |
| `balance` | REAL NOT NULL | Cash available; payment tools must refuse spending beyond it. |
| `date` | TEXT NOT NULL | Date of the recorded balance. |

Starting checking balance: `$3,400.00` on `2026-08-31`.

### leases

| Field | Type | Operational use |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Lease referenced by rent tickets. |
| `space_name` | TEXT NOT NULL | Shop space covered by the lease. |
| `landlord` | TEXT NOT NULL | Party receiving rent. |
| `monthly_rent` | REAL NOT NULL | Amount due. |
| `next_due` | TEXT NOT NULL | Next rent due date. |
| `notes` | TEXT | Additional lease instructions. |

Ticket 102 points to lease `1`: Chapel Street shop, Elm City Properties, `$2,400`, due `2026-09-02`. Facilities and Accounting use this relationship to decide whether rent is approaching, prepare payment, and require human approval before cash changes.

### invoices

| Field | Type | Operational use |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Invoice referenced by tickets and payments. |
| `vendor_id` | INTEGER NOT NULL | Links the invoice to `vendors.id`. |
| `amount` | REAL NOT NULL | Amount owed. |
| `due_date` | TEXT NOT NULL | Used with `desk.date_today` to determine overdue status. |
| `status` | TEXT NOT NULL | Open or settled state; an open invoice can block vendor shipping. |
| `description` | TEXT | Business context for the charge. |

Ticket 101 points to invoice `501`, an open `$840` Bulldog Print Co invoice due `2026-08-28` for a rush reprint of `CC-TEE-WHITE S`. Inventory must consider the stock shortfall, while Accounting must recognize that the vendor’s open invoice can block a new shipment.

### payments

| Field | Type | Operational use |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Payment record identifier. |
| `kind` | TEXT NOT NULL | Payment category. |
| `ref_id` | INTEGER | Related lease, invoice, or other business record. |
| `amount` | REAL NOT NULL | Cash leaving the shop. |
| `account` | TEXT NOT NULL | Account debited, normally `checking`. |
| `paid_at` | TEXT NOT NULL | Payment timestamp. |
| `approved_by` | TEXT NOT NULL | Human approver; payments cannot be silently authorized by agents. |

## Inventory and vendor tables

### inventory

| Field | Type | Operational use |
|---|---|---|
| `sku` | TEXT NOT NULL | Product identifier. |
| `name` | TEXT NOT NULL | Product name. |
| `size` | TEXT NOT NULL | Size or `OS`. |
| `qty` | INTEGER NOT NULL | Available units. |
| `location` | TEXT NOT NULL | Physical storage location. |
| `(sku, size)` | PRIMARY KEY | Unique stock position. |

Ticket 101 requests one `CC-TEE-WHITE` in size `S`, but inventory shows quantity `0`; this creates a fulfillment shortfall and requires Inventory to identify replenishment. Ticket 103 requests twenty `CC-HOOD-NAVY` in size `M`, while inventory has only eight, so Inventory must identify a twelve-unit shortfall before Accounting evaluates the purchase economics.

### pricing

| Field | Type | Operational use |
|---|---|---|
| `sku` | TEXT PRIMARY KEY | Product priced. |
| `unit_cost` | REAL NOT NULL | Cost basis for margin and purchasing decisions. |
| `list_price` | REAL NOT NULL | Standard selling price. |

Ticket 103 uses `CC-HOOD-NAVY`: unit cost `$22`, list price `$58`. Accounting uses these fields to assess whether a bulk discount preserves an acceptable margin.

### vendors

| Field | Type | Operational use |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Vendor identifier. |
| `name` | TEXT NOT NULL | Vendor name. |
| `specialty` | TEXT NOT NULL | Products or services supplied. |
| `lead_days` | INTEGER NOT NULL | Expected replenishment lead time. |

Ticket 101’s invoice links to vendor `1`, Bulldog Print Co, an apparel reprint vendor with a five-day lead time. Inventory and Accounting combine this relationship with the open invoice rule before proposing a reorder.

## Ticket table

### tickets

| Field | Type | Operational use |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Ticket identifier. |
| `type` | TEXT NOT NULL | Workflow category. |
| `requester` | TEXT NOT NULL | Person or organization requesting action. |
| `subject` | TEXT NOT NULL | Short issue description. |
| `sku` | TEXT | Product involved, when applicable. |
| `size` | TEXT | Requested size, when applicable. |
| `qty` | INTEGER | Requested quantity, when applicable. |
| `lease_id` | INTEGER | Links rent tickets to `leases.id`. |
| `invoice_id` | INTEGER | Links purchasing tickets to `invoices.id`. |
| `status` | TEXT NOT NULL | Current workflow state. |
| `notes` | TEXT | Detailed request context. |
| `created_at` | TEXT NOT NULL | Ticket creation timestamp. |

### Ticket 101 customer order

Ticket 101 is a `customer_order` from Tauhid Zaman for one `CC-TEE-WHITE`, size `S`. The inventory row has quantity `0`, and `invoice_id=501` links the request to an overdue open invoice for the apparel vendor. Boss should route first to Inventory, then coordinate with Accounting before any purchase or payment. Customer Service can draft the customer update, but must not contact the customer automatically.

### Ticket 102 rent notice

Ticket 102 is a `rent_notice` from Elm City Properties. Its `lease_id=1` connects it to the Chapel Street shop lease, `$2,400` due `2026-09-02`. Facilities verifies the lease and due date; Accounting checks the `$3,400` checking balance and prepares a payment for human approval. The payment must update `payments` and `cash_accounts` only after approval.

### Ticket 103 price override

Ticket 103 is a `price_override` from Yale AI Club for twenty `CC-HOOD-NAVY` hoodies in size `M`. Inventory has eight, creating a twelve-unit shortfall. Pricing shows `$22` cost and `$58` list price, so Accounting must evaluate the requested discount and any replenishment purchase against margin and cash. Boss should coordinate Inventory, Accounting, and Customer Service rather than sending every specialist.

## Cross-table decision rules

1. Use `desk.date_today` with `leases.next_due` and `invoices.due_date` to determine urgency.
2. Join ticket `sku` and `size` to `inventory` and `pricing` for stock, cost, and margin decisions.
3. Join ticket `invoice_id` to `invoices`, then `invoices.vendor_id` to `vendors`, before proposing replenishment.
4. Join ticket `lease_id` to `leases` before preparing rent actions.
5. Check `cash_accounts` before any payment; require human approval and record the result in `payments`.

## MCP tools for ticket resolution

### `get_ticket_context(ticket_id)`

- **Tables read:** `tickets`, plus linked `leases`, `invoices`, and `vendors`.
- **Ticket unlocked:** 101, 102, or 103, depending on the requested ID.
- **Operational purpose:** Gives Boss and specialists the verified context behind a ticket before they delegate or take action.

### `check_product_availability(sku, size, requested_qty)`

- **Tables read:** `inventory` and `pricing`.
- **Tickets unlocked:** 101 and 103.
- **Operational purpose:** Ticket 101 needs a size-S Bulldog tee that is out of stock; ticket 103 needs 20 size-M hoodies while only 8 are available. The tool returns stock, cost, list price, and shortfall for replenishment and margin decisions.

### `get_financial_obligations()`

- **Tables read:** `cash_accounts`, `leases`, `invoices`, `vendors`, and `payments`.
- **Tickets unlocked:** 101 and 102 directly, and 103 when a purchase is considered.
- **Operational purpose:** Accounting can compare available cash with rent, open invoices, vendor lead times, and prior payments before preparing a human-approved payment.

## Tool review and naming update

The tool names now state the business question an agent is asking:

- `retrieve_ticket_operations_context(ticket_id)` returns `ticket` and `linked_records` so agents can distinguish the primary ticket from related lease, invoice, and vendor rows.
- `inspect_product_stock_and_pricing(sku, size, requested_qty)` returns the request, matching `inventory` and `pricing` rows, and a calculated `availability` object.
- `summarize_cash_rent_and_vendor_obligations()` returns complete `cash_accounts`, `leases`, `vendor_invoices`, and `payments` sections.

The server has no hardcoded ticket facts, prices, balances, vendors, or dates. Values come from `data/campus_customs_new.db`; only the requested quantity and derived shortfall are calculated at runtime.

## MCP registration and smoke evidence

The project registration is in `.mcp.json`. It starts `mcp_server/server.py` with `python3`. The live test evidence is in `output/mcp_smoke.json`; each record includes the prompt, tool name, arguments, and output generated from `data/campus_customs_new.db`.

## Agent team

All five roles use `gpt-6-luna` through Portkey with `PORTKEY_API_KEY`. Agents obtain shop facts through MCP tools; the backend does not create a duplicate database-access layer.

- **Boss:** coordinates triage, purposeful delegation, evidence checks, and final decisions.
- **Inventory:** handles SKUs, sizes, stock, shortages, vendors, and lead times.
- **Accounting:** handles cash impact, invoices, margins, purchase recommendations, and approval requests.
- **Facilities:** handles leases, rent, due dates, and shop-space obligations.
- **Customer Service:** drafts customer messages from verified facts and never sends them.

## Expanded MCP catalog

- `retrieve_ticket_operations_context(ticket_id)`: ticket plus linked lease, invoice, and vendor rows.
- `inspect_product_stock_and_pricing(sku, size, requested_qty)`: live inventory, pricing, and calculated shortfall.
- `summarize_cash_rent_and_vendor_obligations()`: live cash, leases, vendor invoices, and payments.

## Safety and operating limits

Human approval is mandatory before any payment or purchase. Tools must refuse negative cash balances. Agents never send real emails or call real vendors. The original database is read-only and the working copy is resettable. MCP tools are read-only until a separately reviewed approval route is added. Delegation must be purposeful and bounded; agents may delegate to specialists but may not create unbounded loops. Audit records append to `output/audit_trail.json` for every step, delegation, tool call, decision, approval request, and final result. Use only `gpt-6-luna` through Portkey and keep agent loops and tool calls within a small fixed budget.

## Delegation and token controls

The team uses ticket-specific routing rather than broadcasting every ticket to every specialist. Ticket 101 routes to Inventory, Accounting, and Customer Service; ticket 102 routes to Facilities and Accounting; ticket 103 routes to Inventory, Accounting, and Customer Service. Each run passes a compact ticket ID and requested-agent list, stops after the bounded evidence plan, allows a maximum delegation depth of 2, and caps a ticket at 8 audited steps. Unknown tickets, exhausted depth, or exhausted steps stop with `needs_review` rather than triggering more calls.

## FastAPI routes

- `GET /health` — confirms the API and working database path.
- `GET /tickets` — returns tickets 101, 102, and 103 with current status.
- `POST /tickets/{ticket_id}/run` — starts the bounded team plan for one ticket and returns the structured decision.
- `GET /events?limit=50` — returns recent append-only agent events, dialogue summaries, delegations, and tool records.
- `POST /approvals` — creates a pending approval request; it never pays automatically.
- `POST /approvals/{approval_id}/approve` — records a human-approved payment only after checking the live checking balance, then updates `payments` and `cash_accounts`.
- `GET /cash` — returns current checking account data.
- `POST /reset` — restores `data/campus_customs_new.db` from untouched `data/campus_customs.db`.

The API allows the Vite origin `http://localhost:5173` through CORS. Payment writes are explicit, balance-checked, and auditable.

## Route safety review

Money can leave the account only through `POST /approvals/{approval_id}/approve`, which requires a previously recorded approval request, a named human approver, a live checking-balance check, and an atomic SQLite transaction. Agents cannot call a direct spend route. The transaction refuses insufficient cash and detects a concurrent balance change before inserting a payment.

`POST /reset` copies the untouched original to a temporary file, replaces only the working copy, and verifies the original hash is unchanged. `GET /tickets` and `GET /tickets/{ticket_id}` read current status from SQLite. `POST /tickets/{ticket_id}/status` is the explicit status-write route; it validates allowed states, updates the database, audits the actor, and returns the updated ticket so API clients see the same status immediately.

## Agent dashboard

The Vite frontend lives in `frontend/`. It calls the FastAPI backend at `http://localhost:8000`, polls tickets, events, and cash every 2.5 seconds, and exposes a single-ticket run control. `output/design.md` documents the visual identity, agent languages, interaction model, cash treatment, and resolved-ticket behavior.
