"""FastMCP server for Campus Customs retail operations."""
from pathlib import Path
import sqlite3
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError:  # Keep import errors clear when setup is incomplete.
    FastMCP = None

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"


def _query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Working database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    rows = _query(sql, params)
    if not rows:
        raise ValueError("No matching record found")
    return rows[0]


def retrieve_ticket_operations_context(ticket_id: int) -> dict[str, Any]:
    """Return a ticket and its linked lease, invoice, vendor, and cash context."""
    ticket = _one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    lease = _query("SELECT * FROM leases WHERE id = ?", (ticket.get("lease_id"),)) if ticket.get("lease_id") else []
    invoice = _query("SELECT * FROM invoices WHERE id = ?", (ticket.get("invoice_id"),)) if ticket.get("invoice_id") else []
    vendor = _query("SELECT v.* FROM vendors v JOIN invoices i ON i.vendor_id=v.id WHERE i.id = ?", (ticket.get("invoice_id"),)) if ticket.get("invoice_id") else []
    return {"ticket": ticket, "linked_records": {"lease": lease, "invoice": invoice, "vendor": vendor}}


def inspect_product_stock_and_pricing(sku: str, size: str, requested_qty: int = 1) -> dict[str, Any]:
    """Check stock and pricing for a SKU/size and calculate any shortfall."""
    if requested_qty < 1:
        raise ValueError("requested_qty must be at least 1")
    stock = _one("SELECT * FROM inventory WHERE sku = ? AND size = ?", (sku, size))
    pricing = _one("SELECT * FROM pricing WHERE sku = ?", (sku,))
    return {"request": {"sku": sku, "size": size, "requested_qty": requested_qty}, "inventory": stock, "pricing": pricing, "availability": {"available_qty": stock["qty"], "shortfall_qty": max(0, requested_qty - stock["qty"])}}


def summarize_cash_rent_and_vendor_obligations() -> dict[str, Any]:
    """Return current cash, leases, invoices, and recorded payments for approval decisions."""
    return {"cash_accounts": _query("SELECT * FROM cash_accounts"), "leases": _query("SELECT * FROM leases"), "vendor_invoices": _query("SELECT i.*, v.name AS vendor_name, v.specialty AS vendor_specialty, v.lead_days FROM invoices i JOIN vendors v ON v.id=i.vendor_id"), "payments": _query("SELECT * FROM payments")}


if FastMCP is not None:
    mcp = FastMCP("campus-customs-operations")
    mcp.tool()(retrieve_ticket_operations_context)
    mcp.tool()(inspect_product_stock_and_pricing)
    mcp.tool()(summarize_cash_rent_and_vendor_obligations)

    if __name__ == "__main__":
        mcp.run()
else:
    mcp = None

__all__ = ["mcp", "retrieve_ticket_operations_context", "inspect_product_stock_and_pricing", "summarize_cash_rent_and_vendor_obligations"]
