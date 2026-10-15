# Campus Customs Dashboard Design

## Layout

The dashboard uses a warm editorial desk layout: a masthead establishes the operating context, the checking balance stays visible at the top, a narrow ticket rail supports quick selection, and a larger workspace shows the selected ticket’s agent activity.

## Visual system

The palette uses warm paper tones, navy ink, terracotta, amber, green, and lavender. A subtle dot texture gives the page a paper-and-receipt feel without competing with the data. Cards use restrained borders and small editorial labels so the interface feels like a boutique operations ledger rather than a generic admin panel.

## Agent styles

Boss uses navy command-stamp styling. Inventory uses amber and a barcode-like grid icon. Accounting uses green ledger styling. Facilities uses terracotta and a house mark. Customer Service uses lavender and an envelope mark. The same colors identify each agent in the activity trail.

## Interactions

The ticket rail lets a human select one of tickets 101, 102, or 103. The Run Agent Team action starts the selected backend route. The activity trail refreshes every 2.5 seconds, showing event type, agent, summary, MCP tool name when present, and timestamp. Waiting, running, and error states are explicit.

## Cash and approvals

Checking balance is visible in the masthead and refreshes from the API. Approval controls belong to the backend’s explicit human-approval route; the dashboard does not silently spend money. This keeps the money line visible and deliberate.

## Resolved tickets

Ticket status is displayed as a compact status pill in the ticket rail. Resolved tickets remain visible for operational continuity, while the event trail preserves the work that led to resolution.

## Creative choices

The desk is designed to feel calm under pressure. Clear agent identities, restrained motion through the live pulse, short event summaries, and generous spacing let a human follow a multi-agent handoff without reading a wall of logs.

## Refinement pass

The desk now uses a sticky control bar, stronger focus rings, ticket hover and selected transitions, live-feed labeling, animated status lights, a loading spinner, clearer event spacing, readable timestamps, and mobile-specific layout rules. The run action has a tactile pressed state and accessible label. Ticket buttons expose their selection state to assistive technology, while events remain concise enough to scan during a busy shop day.

The refinement also adds a high-contrast approval queue inside the workspace. Pending money requests are derived from the audit feed, show the ticket and amount, and require an explicit “Approve” action; saving feedback and error messaging keep the supervisor oriented while the backend records the decision.
