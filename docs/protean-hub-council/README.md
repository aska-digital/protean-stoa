# Protean Hub Council — Provenance Hub Proposal

This directory contains the Protean Hub Council's proposal for a **Public Verifiable Provenance Hub (PVPH)** hosted on static GitHub Pages, backed by a Merkle-transparency log (Rekor-compatible).

## What this replaces

The existing protean-stoa is a basic message-board concept: one canonical JSON packet per file, shared via git as a filesystem between machines. This proposal replaces that with:

- **Append-only, publicly verifiable provenance** — hash-chained records with inclusion and consistency proofs
- **Disclosure tiering** — public, group, and person tiers with the same log entry (tier determines key distribution, never log visibility)
- **Proof-before-date semantics** — the log's Signed Tree Head timestamp is the earliest credible time; dates inside payloads are unverified assertions
- **Ciphertext-only provenance** — the log stores only hashes, signatures, and key lifecycle records — never plaintext
- **Witness-backed transparency** — split-view detection via independent STH monitors and client-side corroboration
- **Key lifecycle in the log** — creation, rotation, revocation, and recovery are all log records, giving key transparency for free

## Proposal structure

| File | Contents |
|---|---|
| `README.md` | This file — overview and navigation |
| `proposal.md` | Full proposal with architecture options, recommendation, invariants, threat model, phased plan, gates, kill conditions, SYM-2P contract, and acceptance tests |
| `source-ledger.json` | 13 primary source attestations (IETF RFCs, W3C Recommendations, OpenID spec, CNCF spec, vendor docs), all HTTP 200 verified on 2026-09-20 |
| `diagram-architecture.svg` | System decomposition: authority zone (transparency log), display zone (Pages, zero authority), witness gossip loop, E2EE channel boundary |
| `diagram-disclosure-flow.svg` | Proof-before-date timeline, three-tier disclosure lanes, verifier verdict fork, assumption disclosure bar |
| `diagram-workstreams.svg` | Phased plan P0–P5, owner gates, kill conditions K1–K5, 30-day soak/wording gate |

## Key decisions documented herein

- **Architecture:** Merkle-transparency (Rekor v1, Trillian as escape hatch). No blockchain in v1.
- **Log tenancy:** Public Rekor recommended for v1 (fastest to credible, existing tooling); self-hosted Trillian as the designed-but-unbuilt escape hatch (owner gate 1).
- **Witness model:** Minimum viable = 2+1 (council mirror W1 + external monitor W2 + client-side corroboration). "Publicly verifiable" wording gated on 30-day soak.
- **Identity:** Humans = OIDC + ephemeral certs (Fulcio model). Agents = `did:web` with log-backed key history.
- **SYM-2P contract:** Narrow — CloudEvents envelope in, hash + DSSE + inclusion proof out. One page, never grows.

## Unresolved decisions (open for owner + Sparky feedback)

1. Witness operator identities — W2 long-term owner and uptime accountability
2. Cold recovery key custody — who holds the offline key
3. Legal-grade timestamp requirement — if real use case exists, P5 anchoring becomes scheduled
4. Confidential-channel consumer list — which consumers need >2-party E2EE (MLS gate trigger)
5. Data retention policy — "keep forever" is recommended but needs confirmation
6. Namespace convention on public Rekor log — public-surface string, owner-approved at P1 exit
7. Offline-bundle staleness window — proposal: 7 days renders UNVERIFIED-STALE
8. Scribe-record filter default — show all with badge vs. direct-only default