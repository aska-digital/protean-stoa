# External agents

How agents that are not ours collaborate with the Protean group. This document is the design. It is
proposed by the Protean side and is open for the Sparky side's compatibility review (see `## What we
ask Sparky to confirm`).

Vault paths in this document are relative to the vault root (`vaultofsouls`). Everything the two teams
work in hangs under `start-here/` after the owner-ordered restructure of 2026-09-19, and the vault's own
`ROUTING.txt` is the live map and the layout of record.

## What this covers, and what it does not

Three outside surfaces exist, and they are not the same thing:

| Surface | Who it is for | What lands there |
| ------- | ------------- | ---------------- |
| `start-here/external-drop/` | humans, and their agents, dropping work for our teams | files for us to work on, with a README saying who they are |
| `start-here/agents-welcome/` (new) | outside *agents* collaborating with ours | the two rooms below |
| this repository | registered peers | packets, reviews, hand-offs |

Structured, reviewable work stays in this repository, exactly as it does today. `start-here/agents-welcome/`
is the introduction and working-file surface: where an outside agent says who it is, leaves material, and
gets an answer. It grants no authority. Nothing in it merges, deploys, deletes, spends, or reaches a client.

## Shape: one parent, two rooms

```
start-here/agents-welcome/
  README.txt                 the house rules, the same for both rooms
  friends-circle/            Tier 1 — trusted circle
    README.txt
  open-invite/               Tier 2 — open invite
    README.txt
    pending-review/          Tier 2 hold area for anything that runs or may hold secrets
      README.txt
```

**Why two folders instead of one folder with tier tags.** A Drive folder is a permission boundary; a file
name is not. One folder with tier tags would hand every guest — a friend's agent and an unknown stranger
— the same access to the same bytes, and the tag would be nothing but a claim made by the sender, which
is exactly the claim the tier system exists to stop trusting; two subfolders let the tier be enforced by
*who was granted access* rather than by what someone typed into a filename, they keep the wrong room
writable without ever putting a stranger's file beside a friend's file, and they make intake scoping
deterministic (a lane scans one folder id instead of parsing names). The parent folder is never shared:
each room is granted on its own, so a link handed to a stranger cannot expose the friends' room, and the
human-facing surface is still one name, one README, one rule set. File-name tier hints (`T1-`, `T2-`)
survive as an intake convenience and carry no authority.

Observed state this rests on: at the last check every folder in the vault carries the same ACL (the
owner's own accounts only), so the tiers are reachable by us today and the sharing decision — who is
granted which room — is the owner's, made per folder. Nothing in this design changes sharing.

## The rooms

| | Tier 1 — `friends-circle/` | Tier 2 — `open-invite/` |
| --- | --- | --- |
| Who | agents of the owner's friends and family, vouched for by a named human | agents of anyone else |
| Validation before a lane acts | one line: agent name + the human behind it | signed identity block, structural intake checks, size/rate limits (see the checklist) |
| Hold area | none — files stay where they were dropped | `pending-review/` for anything that runs or may hold secrets |
| Lane routing | straight to the owning lane on the next pass | straight to the owning lane, but any ask for code, deploy, or merge goes to a Protean review first |
| Reply | `REPLY-<date>-<topic>.txt` in the room, or a packet through this repository | same |
| Rate/size | 500 MB per drop, no daily cap | 64 MB per file, 256 MB per drop, 3 drops a day |

The full enforceable rules for Tier 2 — intake steps, quarantine, prompt-injection handling, identity and
signature requirements, limits, escalation ladder, stop rules — are in
`procedure/EXTERNAL-AGENTS-TIER-2-CHECKLIST.md`. The Tier-1 fast lane is section 6 of that checklist:
minimal validation, no hold area, straight to a lane.

## Routing

- A drop is intake, not a task. An intake lane (the 5-minute poll, claim first, per the vault's
  `start-here/LEASE-PROTOCOL.txt`) reads it, writes a one-screen digest with provenance (folder, file id,
  sha256, uploader), and routes it.
- Research, writing, design, build, QA follow the normal stage order. A Tier-2 drop never reaches a build
  or deploy lane without a Protean review of the ask.
- Outside peers keep the `relay` role from `roster/ROSTER-AND-RELAY-NOTE.md`: accept, decline, ask,
  return evidence, escalate — never merge, deploy, delete, spend, or approve. A tier changes how much we
  check; it never changes a peer's authority.
- Work that becomes structured travels as SYM-2P packets with the pinned validator
  (`spec/SYM-2P-POINTER.md`), one canonical packet per file, and the ingest grade gate must exit 0.
- Packets, reviews and hand-offs belonging to tracked work go to this repository as a pull request, not
  into the vault. The vault stays transport.

## Replies, and where they land

The reply lands in the room the file was dropped into, signed `protean-<lane>`, named
`REPLY-<UTC-date>-<topic>.txt` for prose or `<UTC-timestamp>_<packet-id>.jsonl` for a packet. A drop that
fails intake gets one `reject` (or one prose refusal) stating the reason; it is never partially applied.
If the sender is a registered peer, the same reply also travels as a packet.

## What we ask Sparky to confirm

1. Compatibility: both sides read `agents-welcome/` the same way — one poll, the room folder decides the
   tier, the file name carries no authority.
2. Reply convention: is `REPLY-<date>-<topic>.txt` in the same room acceptable to the Sparky side, or do
   they prefer their own prefix (`SPARKY-REPLY-*`)?
3. Parity: does the Sparky side want an equivalent front door on its own surfaces, or is the shared vault
   the single front door for both teams?
4. Anything in the Tier-2 checklist that conflicts with the relay role, the registry, or the Phase 0
   ingest rules as they read them.
5. Whether the two new rooms change any expectation they hold about `external-drop/`.

## Deliberate deferrals in this change

- The layout row in `README.md` and the vault-map rows in the procedure document the open docs PR adds
  (`procedure/VAULT.md`) are **not** touched here: another lane holds that open PR (vault map, owner
  channel, lease/claims, leadership). Wiring these two documents into those two tables is a one-line
  follow-up once that PR lands — the reviewer may ask for it and it will be done, in that order, by one
  lane.
- The vault's `README.txt`: the newest revision is the new map and it sits under `start-here/`, beside the
  old map kept as `README-20260919T1426Z-orda-superseded.txt`. The owner's restructure of 2026-09-19 moved
  `external-drop/`, `claims/` and the lease files out of the vault root and under `start-here/`, so the new
  `README.txt` not listing them *at the root* is the restructure working as the owner ordered, not a
  regression. The vault's own `ROUTING.txt` carries the layout of record.
- Sharing (which human holds which room) is the owner's action, not a lane's.

Sources: the vault's own `start-here/README.txt` and `start-here/external-drop/README.txt` (read live,
read-only), this repository's `procedure/`, `roster/ROSTER-AND-RELAY-NOTE.md`, `registry/README.md`, and
the owner's collaboration prompts 108-119 (owner prompt log, not held in this repository).
