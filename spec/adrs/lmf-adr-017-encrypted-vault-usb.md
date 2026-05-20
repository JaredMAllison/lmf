---
title: "ADR-017: Encrypted USB as Canonical Vault Store"
type: adr
project: LMF
status: accepted
date: 2026-05-07
tags: [adr, lmf, vault, security, architecture]
supersedes: []
---

## Context

The LMF vault is someone's brain — their cognitive prosthetic, their foundation document, their accumulated self-knowledge, tasks, projects, and personal patterns. This is not app data. It is the most sensitive digital artifact a person can have.

The current bootstrap (`bootstrap.ps1`) copies the vault from the USB to `%USERPROFILE%\LMF\vault\` on the host's SSD. This has three problems:

1. **The vault exists in cleartext on the host disk** — readable by anyone with physical or remote access to the machine, by Windows Search indexing, by backup software that sends it to the cloud, by forensic recovery after deletion.
2. **The vault has no canonical location** — it's one copy among several (USB source, host copy, potential backup copies), and truth becomes ambiguous.
3. **Recovery is undefined** — if the host drive dies, the vault dies with it. There is no recovery path.

Backups are traditionally proposed as the solution, but a backup is an attack surface. Every copy of a brain is a risk. The goal is not redundancy through proliferation — it's resilience through a single encrypted canonical store with intentionally limited clones.

## Decision

### Single encrypted USB is the canonical vault store

- The vault lives on an encrypted USB drive. No other copy of vault contents exists in cleartext on any device.
- The USB is encrypted at the block level: **VeraCrypt** (cross-platform, FOSS, audited) or **BitLocker To Go** (Windows-native, simpler UX). Choice deferred to operator during setup.
- `bootstrap.ps1` creates the vault directory on the USB, not on the host. The `vault_path` in `config.yaml` points to a path on the mounted USB (e.g., `D:\vault\`).
- `launch.ps1` checks the USB is mounted and the vault path exists before starting any service. If absent, it fails with "Vault USB not found — insert the drive and try again."
- The orchestrator, init mode, and Cockpit read/write the vault through the mounted drive letter. At no point is vault content persisted to the host SSD.

### Clone destination (content backup)

During init, the operator declares a clone destination — where the encrypted container is mirrored for content recovery if the primary USB is lost or destroyed.

- The destination is operator-chosen: a second USB, an SMB share, a local folder on another machine, a file on a server. Not constrained to a second USB.
- The clone is an encrypted container-level copy, identical to the primary. The clone is never mounted — it exists only as a recovery source.
- Mirror runs on two triggers: (1) on operator-set daily schedule, (2) on clean vault unmount (before USB ejection).
- The orchestrator provides `POST /mirror` (trigger clone) and `GET/POST /schedule` (configure mirror timing). The Cockpit exposes a "Safely eject" button that mirrors before unmounting.
- No vault content ever leaves the encrypted container in cleartext. The clone path is declared during init and stored in `config.yaml` (`clone_path`, `clone_type`, `mirror_time`, `mirror_timezone`).

### SSS recovery key (passphrase recovery)

A 256-bit recovery keyfile is generated during init mode, registered as an additional credential on the encrypted volume. This keyfile is split using Shamir's Secret Sharing (N=3, M=2) over GF(p) where p = 2^127 - 1.

- The operator's vault USB carries Share 1 trivially (the recovery keyfile lives at `operator/recovery.key` on the encrypted volume). The vault IS the first share.
- During init, a built-in wizard distributes Share 2 and Share 3 via operator-chosen channels: SMS (GV integrated), a file download, another LMF instance, email, or printed QR.
- `operator/recovery.yaml` stores the distribution ledger (where each share went), NOT the shares themselves.
- On recovery (passphrase forgotten), the operator provides any 2 of 3 shares via a wizard. The orchestrator's `POST /recover` endpoint reconstructs the keyfile, validates against the stored SHA-256 hash, and permits a passphrase reset via `POST /set-passphrase`.
- The recovery key is a VeraCrypt keyfile slot on the volume — it independently unlocks the same container. The daily passphrase and the recovery key are two separate credentials for the same lock.
- The SSS library is pure Python (stdlib only), deployed as `core/crypto_utils.py`. No external dependencies.

### No host-side vault mirror

- The vault is never copied to the host SSD. `vault_path` in config always points to the mounted USB.
- `bootstrap.ps1` creates the vault directory on the USB only. The `$vaultMarker` pattern checks the USB, not the host.
- `launch.ps1` checks USB presence before starting services.
- `teardown.ps1` warns if USB is still mounted and offers a final mirror before stopping.

### Init mode runs on the encrypted vault

- Init mode's `.proposed/` directory and the final `LOCAL_MIND_FOUNDATION.md` live on the encrypted USB.
- The `[INIT_COMPLETE]` flow writes foundation content to the USB, not the host.
- During setup, the operator is prompted to insert and mount their encrypted USB before init mode begins.

## Consequences

### Enables

- **Brain-yank property:** Pull the USB and the cognitive prosthetic goes with you. Plug into any LMF-capable machine, mount the drive, and pick up exactly where you left off.
- **Physical security boundary:** The vault is offline when not in use. No remote attack can exfiltrate vault contents because the target is not connected.
- **Clear death-and-recovery path:** USB lost → clone the backup USB → continue. Operator needs only the passphrase and the clone. No partial reconstruction from memory.
- **Simple mental model:** "My brain is on the blue USB." There is no ambiguity about where truth lives.

### Forecloses

- **File-level backup tools** (rsync, Time Machine, Windows File History on vault contents). Encrypted container can't be incrementally backed up at file granularity. Backup is always a full clone.
- **Cloud vault sync** (Syncthing, Dropbox, iCloud for vault files). The encrypted container is not mounted in cloud storage. If cloud access is desired, the container file itself could be stored in a cloud drive, but this introduces the attack surface the decision exists to avoid.
- **Instant failover.** If the USB is lost mid-session, the system stops. There is no "continue from host cache" path. This is deliberate — a brain has no cache.

### Trade-offs

- **USB drive failure risk:** Addressed by the clone + SSS recovery passphrase reset. USB reliability is a known quantity — the daily-driver USB should be replaced annually or on SMART warning.
- **Portability constraint:** The operator must carry the USB. Addressed by the brain-yank philosophy — the USB IS the prosthetic. Forgetting it means the system is unavailable, which is acceptable for a cognitive prosthetic (intentionality of use).
- **Encryption key management:** The SSS recovery key removes single-point-of-failure on the daily passphrase. The threat becomes losing 2 of 3 shares simultaneously — a much smaller risk surface.
- **Setup complexity:** The operator must mount the encrypted drive before running setup. The wizard walks through encryption, clone path, mirror schedule, and recovery share distribution in plain language — no jargon, no SSS math exposed.
- **Performance:** USB read/write is slower than NVMe. For a markdown vault (typically < 50 MB even at significant scale), the difference is negligible. All computational work (Ollama inference, Python runtime) runs from the host SSD.
- **Three deployment profiles:** The core code is deployment-agnostic. The same `orchestrator.py` operates identically under native Windows (USB bootstrap), Docker Compose, or `git clone` + manual setup. Deployment-specific logic is confined to `bootstrap.ps1`, `launch.ps1`, Dockerfile, and README respectively.
