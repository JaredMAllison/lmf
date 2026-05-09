# LMF Feature Inventory

Full inventory of features, skills, and memory types. Each entry tagged:
- `[universal]` — part of the agnostic architecture; any instance can implement
- `[instance: Marlin]` — specific to the reference implementation

## Core Architecture Layers

| Layer | Purpose | Tag |
|---|---|---|
| Capture buffer | Frictionless verbatim intake, zero processing | [universal] |
| Surfacing engine | One task at a time, context-filtered | [universal] |
| Temporal layer | Visual/spatial time representation | [universal] |
| Context awareness | Signal-inferred state (location, motion, schedule) | [universal] |
| Notification gate | Urgency × cognitive load ceiling per context | [universal] |
| LMF profile | Structured cognitive self-model; machine-readable frontmatter | [universal] |
| Vault / knowledge base | Persistent flat-file second mind | [universal] |
| Private vault | Personal content fully isolated from ambient context | [universal] |

## Lifecycle Scripts

| Skill | Trigger | Purpose | Tag |
|---|---|---|---|
| init | Profile fields are default | Conversational onboarding | [universal] |
| review-profile | Cron (30 days) | Periodic profile review | [universal] |
| feature-discover | New capability lands | Does this fit your profile? | [universal] |

## Anchor Rituals

| Skill | Purpose | Tag |
|---|---|---|
| open | Morning anchor — ADLs, task surface, inbox, intention | [universal] |
| close | Evening anchor — inbox processing, tomorrow prep | [universal] |

## Capture & Enrichment

| Skill | Purpose | Tag |
|---|---|---|
| capture | Fast verbatim capture to inbox | [universal] |
| enrich | Structured inbox processing | [universal] |
| learn | Capture concepts from sessions | [universal] |
| project-reload | Rapid context restoration for a project | [universal] |
| ttf-push | Push tasks to The Time Factory | [instance: Marlin] |

## Writing Skills (Scribner)

| Skill | Purpose | Tag |
|---|---|---|
| scribe-capture | Fast idea capture to Ideas/ with work linkage | [instance: Scribner] |
| scribe-open | Morning writing alignment | [instance: Scribner] |
| scribe-close | Evening session log | [instance: Scribner] |
| scribe-sprint | Timed writing block with post-session log | [instance: Scribner] |
| scribe-next | Resume-point retrieval for a work | [instance: Scribner] |
| scribe-resistance | Writer's block intervention | [instance: Scribner] |
| scribe-status | Cross-project dashboard snapshot | [instance: Scribner] |
| scribe-world | Lore consistency lookup | [instance: Scribner] |
| scribe-digest | Parse writing technique content against operator's method | [instance: Scribner] |
| scribe-goals | Word count targets and progress tracking | [instance: Scribner] |
| scribe-review | Periodic pattern analysis of writing sessions | [instance: Scribner] |
| scribe-research | Research note capture linked to work | [instance: Scribner] |
