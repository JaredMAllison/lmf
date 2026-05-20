# Local Mind Foundation

A cognitive prosthetic architecture for neurodivergent people. Locally sovereign, self-building, designed around the operator's neurology — not neurotypical defaults.

This is the umbrella repo. It holds the architecture specs, feature inventory, panel registry, profile schemas, init templates, and layout presets that define what LMF is. The actual runtime components live in sibling repos.

## Architecture

LMF is built around a living profile document (`LOCAL_MIND_FOUNDATION.md`) that the assistant draws context from, onboards through conversation, and maintains through review. The operator talks; the system listens, learns, and builds structure around what they say.

## Repo Structure

```
lmf/
├── spec/             Architecture docs, ADRs, design principles
│   ├── adrs/         Decision records (ADR-001 through ADR-NNN)
│   ├── covenant.md   The LMF Covenant — non-negotiable terms
│   └── principles.md Design values
├── profile/          Profile schemas and templates
│   ├── seed.schema.yaml   Close Family seed schema — LOCAL_MIND_FOUNDATION.md profile definition
│   └── templates/        Default profiles per instance type
├── features/         Feature and panel inventory
│   ├── _index.md     All features, tagged universal vs. instance
│   └── panels/       Cockpit panel declarations
│       ├── registry.json
│       └── specs/    One file per panel
├── init/             Init scripts, prompt templates, seed examples
├── layouts/          Cockpit sub-screen layout presets
│   └── presets/      Suggested models (Scriptorium, Command Center, etc.)
└── stack/            Points to the actual runtime repos
```

## The Ecosystem

| Repo | What it is |
|---|---|
| **lmf** (this) | Umbrella — specs, features, schemas, panels |
| [lmf-ollama-obsidian](https://github.com/JaredMAllison/lmf-ollama-obsidian) | Orchestrator runtime — LLM backend, skills, tools |
| [cockpit](https://github.com/JaredMAllison/cockpit) | Frontend HUD — panel-switching UI, tile composer |
| [marlin](https://github.com/JaredMAllison/marlin) | Task surfacing engine |
| [the-time-factory](https://github.com/JaredMAllison/the-time-factory) | Visual balloon calendar |

## Trust Profiles

LMF supports five instance trust profiles, each with different enforcement needs:

| Profile | Example | Enforcement |
|---|---|---|---|
| Personal | Ariel von Marlin | Path scoping only |
| Work | Prosper0 | Cryptographic audit trail |
| Child | Child (future) | Parent-keyed, content policy |
| Household | Household (future) | Peer-optional |
| Close Family | Close Family | Seeded init, no crypto |

## License

MIT
