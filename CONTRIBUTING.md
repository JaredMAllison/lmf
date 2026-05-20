# Contributing to LMF

Contributions flow upstream, not into forks. If you build something that works for you, it likely works for someone else. Send it home.

## Identity & Attribution

Before your first contribution, you'll be asked:

> *"This is going public. How would you like to identify?*  
> *1) Vault name — your instance's display name*  
> *2) Pseudonym — what you'd like to be called (recommended)*  
> *3) Randomized hash — fully anonymous (default)"*

This applies to every touchpoint: PRs, bug reports, feature requests, panel submissions, discussion posts, documentation updates. You can change your choice at any time.

The system defaults to a randomized hash. You opt into visibility — it's never assumed.

## How to Contribute

### Bug Reports
- Include your instance type (Personal, Work, Safer AI, Household, Close Family)
- Include your LMF profile version (from LOCAL_MIND_FOUNDATION.md frontmatter)
- Describe what happened, what you expected, and how to reproduce

### Feature Requests
- Describe the gap, not the solution. "I need to track writing sessions across projects" > "Add a word count panel"
- Tag which instance profile it's for

### Panel Submissions
- Panels declare their valid sizes in `features/panels/registry.json`
- A panel must implement the panel interface (see `features/panels/SPEC.md` — coming)
- Include a brief description of what cognitive gap it fills

### Frame Contributions

A frame is a metaphor set that translates LMF vocabulary into culturally familiar terms. Frames live in `spec/frames/` — one markdown file per frame.

A valid frame document has four required sections, in this order:

1. **Literacy note** — who this frame is for and what prior knowledge it assumes. Be explicit: if it requires gaming background, say so. Operators without that context should know to skip it.
2. **What this frame captures** — what the frame does that plain vocabulary cannot. Name the design decisions the metaphor illuminates. This is the frame's justification, not a glossary.
3. **What this frame falls short on** — honest assessment of where the frame misleads or leaves gaps. No frame covers everything equally well. Name the alternatives where they exist.
4. **Translation table** — a complete mapping from every term in `spec/vocabulary.md` to the frame's equivalent. Every term must have an entry. Use `—` if a term has no natural translation.

Two optional sections are common and encouraged:
- **Where this frame surfaces** — specific moments in the system (init, CONTRIBUTING.md, domain expert introduction) where this frame's language is useful
- **Mix and match** — explicit note that operators are not required to use the frame consistently

Frame contributions are the lowest-barrier upstream contribution in LMF. No code. No schema. Just markdown and honest translation work.

See `spec/vocabulary.md` for the full term list. See `spec/frames/summons.md` for a complete example.

### Documentation
- Architecture docs live in `spec/`
- Schemas live in `profile/`
- Feature inventory lives in `features/`
- Update the relevant sections; don't create new top-level directories without discussion

### Layout Presets
- Add to `layouts/presets/`
- Include: id, name, instance type, one-line description, tab layout with panel IDs
- Presets are starting points, not final configurations — users customize from them

## Code of Conduct

- No judgment about what someone needs support with
- No gatekeeping — if it helps one ADHD writer, it belongs upstream
- Assume good faith and variable capacity

## PR Process

1. Open an issue describing what you're changing and why
2. Fork or work from a branch
3. Reference the issue in your PR
4. Maintainers review within one cycle

## License

By contributing, you agree that your contributions are licensed under MIT.
