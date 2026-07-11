# <SERVICE-NAME>

<ONE-PARAGRAPH PURPOSE>. Owner: <TEAM-NAME>. Part of the demo-shop system.

## Commands
- `npm install` / `npm run build` / `npm test` / `npm run dev` (port <PORT>)

## Conventions
- All cross-service types come from @demo-shop/contracts. Never redefine them locally.
- Errors: RFC 7807 problem+json.
- Events are versioned; never mutate a published schema, add a new version.

## Architecture notes
- <WHAT IT CALLS>
- <WHAT CALLS IT>
- <EVENTS IN/OUT>

## Code-to-docs mapping (used by the docs-drift pipeline)
| Code path | Docs to update |
|---|---|
| src/routes/*.ts | docs/reference/api.md |
| src/events/*.ts | docs/reference/api.md + docs-hub event catalog |
| package.json (contracts version bump) | docs/index.md changelog section |

## Deeper docs
- docs/index.md, docs/reference/api.md, docs/adr/
