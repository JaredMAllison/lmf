# Rupture Recovery System — Design Spec

**Date:** 2026-05-27  
**Author:** Jared Allison (operator) + Claude Code (architect)  
**Status:** Approved — ready for implementation  
**Implementer:** Big Pickle (Dcockpit)  
**Instance:** Marlin (reference) — pattern generalizable to all LMF instances

---

## Context

Jared lost access to Claude Code (quota exhaustion), suffered a toothache with no appointment until August, and had no Ariel daily driver due to unresolved local inference. Combined, these created a 3-week rupture (May 6–27, 2026) with no daily notes and a spiked failure rate. 

There was no system mechanism to detect the silence, no alert to loved ones, and no structured re-entry ritual. This spec closes that gap.

A **rupture** is a named failure mode in an LMF cognitive prosthetic: the operator goes silent. The system should detect it, alert the people who care, and provide a structured healing path on return.

---

## System Overview

Five components across two new LMF features plus vault artifacts:

```
Daily note gap > 2 days
        ↓
rupture-detector (LMF feature)
  - Reads Daily/ for heartbeat
  - Writes rupture_state.json
  - Calls sos-gateway
        ↓
sos-gateway (LMF feature)
  - Reads users.json for recipients
  - FANS OUT over SMTP: carrier email-to-SMS gateways + plain email + optional Ntfy
  - (no Twilio, no googlevoice — free-first, ADR-036)
        ↓
Loved ones receive alert daily until check-in
        ↓
Operator returns → /marlin-rupture skill
  - Reconstructs what happened
  - Guides rupture note writing
  - Hands off to /marlin-open
        ↓
Ruptures/rupture_NN.md (vault artifact)
  - Incident log
  - Personal witness
```

---

## Feature 1: `rupture-detector`

**Location:** `~/git/lmf/features/rupture-detector/`

### Purpose

Runs daily on Gretchen. Detects rupture by checking for Daily/ note heartbeat. Manages rupture state. Calls sos-gateway when rupture is active.

### Files

```
features/rupture-detector/
├── rupture_detector.py     ← main script
├── manifest.json           ← LMF feature manifest
├── systemd/
│   ├── marlin-rupture-detector.service
│   └── marlin-rupture-detector.timer
└── tests/
    └── test_rupture_detector.py
```

### CLI Interface

```
rupture_detector.py [--dry-run] [--config PATH]
```

- `--dry-run`: Print what would happen without sending alerts or writing state
- `--config`: Override default config path (default: `~/.config/marlin/rupture_config.json`)

### Algorithm (`rupture_detector.py`)

```python
# Pseudocode — Big Pickle implements
def main():
    config = load_config()          # ~/.config/marlin/rupture_config.json
    state = load_state()            # ~/.config/marlin/rupture_state.json

    last_note_date = find_last_daily_note(config.vault_path)
    gap = (today - last_note_date).days

    if gap > config.threshold:      # threshold default: 2
        if state.status != "active":
            state.rupture_detected_at = last_note_date
            state.status = "active"
            state.alert_count = 0

        if state.last_alert_sent != today:
            send_sos(gap, last_note_date, config, state)
            state.last_alert_sent = today
            state.alert_count += 1

    elif state.status == "active":
        send_all_clear(config, state)
        state.status = "clear"
        state.cleared_at = today
        state.alert_count = 0

    save_state(state)
```

### State File: `~/.config/marlin/rupture_state.json`

```json
{
  "status": "clear",
  "rupture_detected_at": null,
  "last_daily_note": "2026-05-27",
  "last_alert_sent": null,
  "alert_count": 0,
  "cleared_at": null
}
```

### Config: `~/.config/marlin/rupture_config.json`

```json
{
  "vault_path": "/home/jared/Documents/Obsidian/Marlin",
  "daily_dir": "Daily",
  "threshold_days": 2,
  "recipients_profile": "family",
  "users_config": "/home/jared/.config/marlin/users.json"
}
```

### Systemd Units

**`marlin-rupture-detector.service`:**
```ini
[Unit]
Description=Marlin Rupture Detector
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %h/.lmf/features/rupture-detector/rupture_detector.py
```

**`marlin-rupture-detector.timer`:**
```ini
[Unit]
Description=Run rupture detector daily at 9am

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Tests

- `test_gap_calculation`: gap computed correctly from last note date
- `test_no_rupture`: gap=1, status stays "clear"
- `test_rupture_detected`: gap=3, status transitions to "active", SOS called
- `test_daily_resend`: gap=5, already active, alert_count increments each day
- `test_all_clear`: gap drops to 1 while active, all-clear fires, state resets
- `test_missing_daily_dir`: Daily/ doesn't exist → safe error, no state change
- `test_idempotent`: running twice same day doesn't double-send

---

## Feature 2: `sos-gateway`

**Location:** `~/git/lmf/features/sos-gateway/`

### Purpose

Outbound alert module. Fans out a wellbeing message over SMTP to configured recipients — carrier email-to-SMS gateways (SMS), plain email, and optional Ntfy. Called by rupture-detector. Designed to be callable by any future LMF feature that needs to reach people outside the vault. **Free-first: no paid SMS SDK, no unofficial scraper — see [[marlin-adr-036-rupture-recovery-protocol]].**

### Files

```
features/sos-gateway/
├── sos_gateway.py          ← main module
├── manifest.json
└── tests/
    └── test_sos_gateway.py
```

### Interface

```python
# Called by rupture-detector (and future callers).
# The message is formatted internally (format_alert_message / format_clear_message),
# so callers pass data, not prose.
from sos_gateway.sos_gateway import send_alert, send_clear

send_alert(
    recipients_profile="family",    # key into users.json
    users_config_path="...",
    n=gap,                          # number of days since last heartbeat
    date=last_note_date,            # last daily-note date
)

send_clear(
    recipients_profile="family",
    users_config_path="...",
)
```

### Channels — fan out, not fall through

All channels ride **one transport: SMTP** (the exobrain Gmail account, same creds as the inbound
gateway). For a safety net, send to *every* configured channel at once and only fail if **none**
deliver — a "try A, else B" chain is the wrong topology for an alarm (ADR-036).

- **SMS** — email to carrier email-to-SMS gateways (`<number>@<carrier-domain>`, e.g. `@txt.att.net`,
  `@tmomail.net`). Free, no fragile auth. Carrier resolved from a `CARRIER_GATEWAYS` map in code.
  *Caveat:* US carriers are degrading these gateways; accepted, offset by fanout + email redundancy.
- **Email** — plain email to the recipient's address, same SMTP transport.
- **Ntfy** (optional) — POST to a topic for any recipient who subscribes; free, already in the stack.

Env: `SMTP_USER`, `SMTP_PASS` (Gmail app password); optional `SMTP_HOST`/`SMTP_PORT`/`NTFY_BASE_URL`.
No `GOOGLE_VOICE_*`, no `TWILIO_*`.

### `users.json` recipient schema

```json
{
  "family": {
    "sms": [{"number": "5035551234", "carrier": "att"}],
    "emails": ["family@example.com"],
    "ntfy_topics": [],
    "routes": ["sos"]
  }
}
```

`carrier` must be a key in `CARRIER_GATEWAYS`. Real values are collected from the operator at moot
(Marlin task `collect-sos-contacts-at-moot`) — do not hardcode.

### Tests

- `test_resolve_sms_addresses`: number + carrier → correct gateway address; unknown carrier skipped (not fatal)
- `test_fanout_sends_sms_and_email`: one SMTP send addressed to both the gateway-SMS address and the plain email
- `test_partial_failure_is_ok_if_any_channel_delivers`: SMTP fails but Ntfy delivers → no raise
- `test_all_channels_fail_raises`: every channel fails → clear RuntimeError (not silent)
- `test_recipient_lookup`: correct sms/emails returned for profile
- `test_message_formatting`: N and date interpolate correctly

---

## Vault Artifacts (Marlin-instance)

These live in the Marlin vault. They are not LMF features — they are instance content.

### `Ruptures/` directory

New vault directory. Not surfaced by marlin.py. Not enriched. Permanent record.

**`Ruptures/_template.md`:**
```markdown
---
title: "Rupture NN — Month YYYY"
type: rupture
date: YYYY-MM-DD
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
gap_days: N
root_causes: []
status: active  # active | recovering | resolved
tags: [rupture, recovery]
---

## Incident Log

### Timeline
<!-- What broke, when -->

### Root Causes
<!-- Why it broke -->

### Blast Radius
<!-- What was affected -->

### Recovery Status
<!-- What's resolved, what remains -->

---

## Personal Witness

<!-- Jared's words only. Verbatim. No paraphrase. What it cost. What held. What was learned. What you'd change. -->
```

### `Ruptures/rupture_01.md`

Populate with the May 2026 rupture content from this design session's reconstruction:

- **Period:** 2026-05-06 to 2026-05-27 (21 days)
- **Root causes:** quota-exhaustion, git-stash-vault-wipe, toothache, ariel-inference-gap
- **Status:** recovering

Big Pickle: write the incident log from the reconstruction in the design session. Leave the Personal Witness section blank — Jared writes that in his own words during `/marlin-rupture`.

### `System/Skills/marlin-rupture/SKILL.md`

Healing ritual. Steps:

1. **Orient** — Run `date`, compute gap from last daily note. Name the rupture period.
2. **Reconstruct** — Read daily notes from rupture window. Report what was happening.
3. **System check** — Verify marlin.py, webhook.py, Ariel, Knowledge Loom are healthy.
4. **Present summary** — Here is what broke. Here is what recovered. Here is what's still open.
5. **Incident log** — Guide writing of the rupture note incident log section. Auto-populate from reconstruction if possible.
6. **Personal witness** — Stop. Ask Jared to write in his own words: what it cost, what held, what was learned. Verbatim only — no paraphrase. (Mirror the Day Close rule.)
7. **Triage** — What needs attention in the next 24h? Produce a short prioritized list.
8. **Hand off** — Invoke `/marlin-open` to complete day start.

Trigger phrases: `marlin-rupture`, `healing ritual`, `I'm back`, `returning after a break`, `recovery ritual`.

### `Decisions/marlin-adr-036-rupture-recovery-protocol.md`

Use standard ADR template. Key content:

- **Context:** Cognitive prosthetics fail silently when the operator disappears. No detection, no alert, no structured re-entry. The May 2026 rupture (21 days, three root causes) exposed this gap.
- **Decision:** Formalize "rupture" as a named failure mode. Define it as 2+ calendar days without a Daily/ note (the heartbeat signal). Build detection, alerting, and recovery ritual as first-class LMF components.
- **Consequences:** Loved ones have visibility into operator wellbeing. The operator has a structured return path. Future ruptures are documented and learnable-from rather than silently absorbed.
- **Compliance:** rupture_state.json tracks active/clear state. Systemd timer runs daily. All-clear fires automatically on recovery.

---

## Implementation Sequence (for Big Pickle)

Build in this order — each step is independently testable:

1. **`sos-gateway`** — implement and test in isolation first (mock recipients)
2. **`rupture-detector`** — implement with sos-gateway as dependency; full integration tests
3. **Systemd units** — install and enable on Gretchen via Feature Manager
4. **Vault artifacts** — write skill, template, rupture_01.md, ADR-036
5. **Integration test** — manually set a backdated last_daily_note in rupture_state.json, run detector, verify SOS fires

---

## Verification

End-to-end test:

```bash
# 1. Temporarily set state to simulate rupture
echo '{"status":"clear","last_daily_note":"2026-05-24","last_alert_sent":null,"alert_count":0}' \
  > ~/.config/marlin/rupture_state.json

# 2. Run detector
python ~/.lmf/features/rupture-detector/rupture_detector.py --dry-run

# Expected: prints "RUPTURE DETECTED: 3 days. Would send SOS to family."

# 3. Run without --dry-run against test recipients to confirm delivery
# 4. Create today's daily note → run detector again
# Expected: prints "ALL CLEAR. Would send clear to family. State reset."
```

ADR-036 should be written and readable in Obsidian before Big Pickle closes the branch.

---

## Open Questions (resolved in design session)

| Question | Decision |
|---|---|
| Detection signal | Daily note heartbeat — binary, no inference |
| Alert cadence | Daily until check-in clears rupture |
| Detector location | Standalone LMF feature (not in marlin.py) |
| SOS location | LMF feature (sos-gateway), not Marlin-specific |
| Note structure | Two-part: incident log + personal witness (verbatim) |
| Build doctrine | Everything is an LMF feature from day one |
