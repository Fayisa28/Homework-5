# Campus Customs Multi-Agent Operations

Campus Customs is a small retail operations desk built for Homework 5. A FastMCP server supplies database-grounded shop facts, a FastAPI control center coordinates bounded agent work and approvals, and a React/Vite dashboard lets a supervisor watch tickets, events, cash, and approval requests.

## Project structure

- `AI_prompts.md` — assignment prompt log
- `data/campus_customs.db` — untouched original database
- `data/campus_customs_new.db` — resettable working copy
- `mcp_server/` — read-only FastMCP tools
- `backend/` — FastAPI routes, agent team, models, and audit logging
- `frontend/` — React/Vite/TypeScript dashboard
- `output/` — harness documentation, design notes, run evidence, and standalone boards

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

Copy `.env.example` to `.env` and set a real key locally:

```bash
cp .env.example .env
# edit .env and set PORTKEY_API_KEY
```

`.env` is ignored by Git. Never commit an API key. The agents are configured for `gpt-6-luna` through Portkey only.

## Reset the working database

The original database is preserved. Before a fresh run:

```bash
cp data/campus_customs.db data/campus_customs_new.db
```

Or, with the API running, call `POST http://localhost:8000/reset`.

## Start the MCP server

The local project registration is in `.mcp.json`. To run the server directly:

```bash
python3 mcp_server/server.py
```

It reads only `data/campus_customs_new.db`.

## Start FastAPI

```bash
uvicorn backend.main:app --reload --port 8000
```

The API serves tickets, bounded runs, audit events, cash, explicit approval requests, approval execution, and database reset. No agent can spend money without a human approval request, and the payment route refuses a negative checking balance.

## Start the dashboard

In another terminal:

```bash
cd frontend
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

## Run the three tickets safely

1. Reset `data/campus_customs_new.db` from the original.
2. Start FastAPI and the dashboard.
3. Select tickets 101, 102, and 103 one at a time and use **Run Agent Team**.
4. Review the audit trail and approval queue.
5. Approve a payment only after checking its ticket, amount, and cash impact.
6. Confirm the resulting balance in the Cash display and database.

Customer and vendor communications remain drafts. The dashboard and evidence files do not fabricate fulfillment, shipment, or revenue.

## Verification notes

Both database files are required and present. The backend and MCP paths are resolved from the project root, so they do not depend on the shell's current directory. A repository scan should show no committed `.env` file, API key, or unsupported model name. Run evidence is stored in `output/audit_trail.json`, `output/resolved_tickets.json`, and the standalone HTML records.

## Submission audit limitations

This repository includes the bounded, database-grounded orchestration implementation and prompt specifications. The current environment may not have the packages from `requirements.txt` installed, so run the setup commands above before starting FastAPI or FastMCP. A GitHub URL is intentionally not fabricated: create the public repository, add its remote, and replace the note in `output/github_url.txt` with the real URL.
