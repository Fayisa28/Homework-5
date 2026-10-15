# Campus Customs Multi-Agent Operations

I use this file to record the prompts I type while building my Campus Customs Multi-Agent Operations project. For each problem, I will briefly describe my goal, preserve the prompt I used, and note what the prompt accomplished or what I needed to clarify.

## Problem 1: Vibe Coder Prompts

### My Goal

I am setting up a clear prompt log for the assignment. I will add each prompt as I work and keep the notes in my own words.

### Prompt Log

#### Prompt 1

> _I will add my first prompt here._

**What this accomplished:** I will briefly explain what this prompt asked the vibe coder to do.

### Follow-Up Notes

I will add a follow-up prompt here if the first response leaves something incomplete or unclear. I will also explain what was missing and how the follow-up addressed it.

## Future Problems

### Problem 2

**What I am working on:** I will add a short description when I begin this problem.

**Prompt log:** I will add my prompts and accomplishment notes here.

### Problem 3 and Later

I will add one clearly labeled section for each later problem as I begin it. Each section will include my goal, prompt blocks, accomplishment notes, and follow-up notes when needed.

## Problem 2: Study the Campus Customs Database

### My Goal

I inspected every table, field, type, and relationship in the original database, studied tickets 101–103, and created a separate working copy so the original remains recoverable.

### Prompt Log

#### Prompt 1

> I inspected every table, column, type, and relationship in `data/campus_customs.db`. I studied tickets 101, 102, and 103 and traced their links to inventory, pricing, vendors, leases, invoices, payments, cash accounts, and other relevant tables. I preserved the original database, created `data/campus_customs_new.db` as the working copy, and began `output/harness.md` with field-by-field operational notes.

**What this accomplished:** I documented the verified schema, ticket relationships, starting cash, inventory shortfalls, vendor constraints, rent timing, and pricing decisions in the operations harness.

### Follow-Up Notes

I added ticket-specific explanations to the harness so the agents can connect each database relationship to a concrete business decision.

## Problem 3: Build the MCP Server

### My Goal

I built a read-only FastMCP server that uses only the working database and exposes three structured tools tied to the open tickets.

### Prompt Log

#### Prompt 1

> I built a clean FastMCP server in `mcp_server/` connected only to `data/campus_customs_new.db`. I added tools for ticket context, product availability, and financial obligations, with validation, structured outputs, and clear errors. I documented the tools in the harness and server README without changing the original database.

**What this accomplished:** I created the MCP server, tool catalog, setup documentation, and ticket-specific harness entries.

### Problem 3 Review Note

I reviewed the tools as an operations manager, renamed them around the decisions agents need to make, and made their JSON sections explicit. I verified the sample calls against the working SQLite database and removed any dependence on hardcoded business facts.

## Problem 4: Add the MCP Server and Test Each Tool

### My Goal

I registered the local FastMCP server with the project and tested each renamed tool against the working database.

### Prompt Log

#### Prompt 1

> Register the MCP server in the project’s local `.mcp.json`, test each MCP tool against `data/campus_customs_new.db`, and save the exact prompts, tool names, arguments, and returned outputs as auditable evidence in `output/mcp_smoke.json`.

**What this accomplished:** I created the project MCP registration and generated live smoke-test evidence for all three tools.

## Problem 5: Build the Agent Team and Grow the MCP Tools

### My Goal

I created five distinct agent roles with detailed prompts, shared Pydantic models, a clear backend team module, and append-only audit logging. The team is grounded in MCP evidence and uses only `gpt-6-luna` through Portkey.

### Prompt Log

#### Prompt 1

> Build Boss, Inventory, Accounting, Facilities, and Customer Service with detailed role prompts, shared models, MCP-only shop facts, purposeful delegation, audit logging, safety controls, and complete documentation.

**What this accomplished:** I added the five prompts, shared models, agent profiles, ticket orchestration, audit helper, harness safety section, and MCP documentation updates.

### Problem 5 Architecture Review

I reviewed the team for unnecessary complexity. I added ticket-specific routing, compact context, a maximum delegation depth of 2, an eight-step ticket cap, and explicit stop results for unknown tickets or exhausted limits. The audit trail still records each delegation and stopping decision.

## Problem 6: Plan the Three Tickets

### My Goal

I created a standalone operations planning page with ticket-specific Expected plans, empty Actual sections, and Cash and Reflection tabs reserved for later work.

### Prompt Log

#### Prompt 1

> Build a polished `output/desk_tickets.html` planning page with boutique styling, clear tabs, agent badges, specific routing for tickets 101–103, Expected and Actual sections, and blank Cash and Reflection tabs.

**What this accomplished:** I created the double-clickable operations desk page with evidence-based sequences and clear visual separation between planned and completed work.

## Problem 7: Backend Routes

### My Goal

I built the FastAPI control center with structured ticket, event, approval, cash, and reset routes. Payment routes require human approval and refuse insufficient cash.

### Prompt Log

#### Prompt 1

> Build backend/main.py with documented FastAPI routes for ticket status, bounded agent runs, recent audit events, approval requests, human-approved payments, cash balance, and database reset. Add Vite CORS and make all writes explicit and safe.

**What this accomplished:** I added the API control center, approval safeguards, live balance checks, payment and cash updates, reset behavior, and harness route documentation.

## Problem 8: Agent Dashboard

### My Goal

I created a React + Vite + TypeScript dashboard with a boutique command-center visual system, live backend refresh, ticket selection, agent identities, event activity, status states, and visible cash context.

### Prompt Log

#### Prompt 1

> Build a warm editorial Campus Customs dashboard in `frontend/` connected to the FastAPI backend. Show tickets, agent activity, delegations, MCP tools, approvals, cash, errors, and resolved states with distinct visual languages for each agent. Document the design in `output/design.md`.

**What this accomplished:** I created the Vite frontend shell, live polling dashboard, responsive styling, agent-specific cards, activity trail, cash display, and design documentation.
