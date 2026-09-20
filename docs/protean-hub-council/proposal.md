# Protean Hub Council — Public Verifiable Provenance Hub Proposal

**Proposal date:** 2026-09-20 (UTC)
**Author:** Protean Hub Council (Hazen research, Leo architecture, Frida UX/visuals, Mozi build)
**Status:** PROPOSAL — UNMERGED. Owner review required.

---

## 0. Reading key

Claims carry exactly one tag:

- **FACT [S#]** — attested by a primary source in `source-ledger.json`, HTTP 200 verified on 2026-09-20.
- **RECOMMENDATION** — Council judgment grounded in cited facts.
- **ASSUMPTION** — premise the proposal rests on; must be confirmed before the dependent phase proceeds.
- **OPEN** — cannot be decided by architecture/design seats; requires owner or Council decision.

---

## 1. Executive summary

This proposal replaces the current protean-stoa message-board concept with a **Merkle-transparency architecture**: one append-only transparency log (Rekor-compatible, public instance first) as the single source of truth, a static GitHub Pages site that is a pure verifier/display surface with zero authority, and CT-style independent witnesses for split-view detection.

**FACT:** Provenance that the public can verify without trusting the hub operator requires the same primitive that Certificate Transparency (CT) proved at internet scale: an append-only, Merkle-tree log with inclusion and consistency proofs, plus independent monitors/gossip. CT is specified in RFC 6962 (experimental) and RFC 9162 (Proposed Standard). [S1][S2]

**FACT:** Sigstore's Rekor provides a general-purpose, immutable transparency log for software artifacts with a REST API and monitor tooling. It is the closest production analogue to a "provenance hub" without a blockchain. [S3]

**FACT:** GitHub Pages is static-only — no server-side code, no database, no long-running processes. Any "hub" hosted there must be a static front-end over externally-hosted append-only storage. [S6]

**RECOMMENDATION:** Split into two decoupled workstreams with a narrow contract:

- **Workstream A — Public Verifiable Provenance Hub:** static Pages site + externally-anchored transparency log. Ships first.
- **Workstream B — SYM-2P Rework:** protocol revision (E2EE, selective disclosure, identity) decoupled from the hub's release cycle.

---

## 2. Architecture options considered

### Option 1 — Third-party transparency stack (public Rekor + Pages verifier)

Hub records are DSSE-signed and written to the public Sigstore Rekor log; the Pages site and a standalone CLI verifier fetch STHs and inclusion proofs and verify client-side; independent monitors mirror STHs.

- FACT [S3]: Rekor is a production Trillian-backed log with REST API and monitor tooling; public instance live.
- FACT [S1][S2]: inclusion + consistency proofs are the proven primitives; RFC 9162 is the Proposed Standard.
- FACT [S6]: Pages serves static content only; all mutation must hit external APIs — Option 1 fits natively.
- **Pros:** fastest to credible, existing clients (`rekor-cli`, `cosign`), monitor automation exists.
- **Cons:** shared tenancy (anyone can write), dependence on Sigstore ops availability, namespace must be convention-enforced.

### Option 2 — Self-sovereign log (Trillian + own personality + own witnesses)

Same record schema, but the log is a Council-operated Trillian deployment behind a small write API.

- FACT [S12]: Trillian / verifiable-data-structures ecosystem supports bespoke logs with the same Merkle guarantees.
- **Pros:** sovereignty, custom payload validation, no shared-tenant noise.
- **Cons:** you operate the log — without independently operated witnesses it degrades to a trusted database; real ops cost (VM, uptime, on-call).

### Option 3 — Git-native hash chain (append-only JSONL in a repo)

Each entry chains `prev_hash = SHA256(prev_entry)`; branch protection attempts to enforce append-only.

- **Pros:** perfect static fit, zero external dependency.
- **Cons:** RECOMMENDATION **reject as source of truth.** No efficient inclusion or consistency proofs without a full scan; no STH to gossip; force-push and GitHub account compromise both rewrite history. Retained only as a convenience display mirror.

### Decision

**RECOMMENDATION: Option 1 for v1, with Option 2 designed in as the escape hatch.** The record schema, DSSE envelope, and verification algorithm are identical under both options — only the log endpoint and operator differ. Option 3 is demoted to mirror-only.

**OPEN — Log tenancy final choice:** Owner gate 1. Public Rekor start is a recommendation; A2 costs money/ops.

---

## 3. Core concept: proof-before-date / existence semantics

**RECOMMENDATION (invariant I2):** Every timestamped claim in the system is separated into a *claim* and an *existence proof*. A record may say "this artifact was created on date D" — but the only evidence the system vouches for is: the record's hash was included in the log at or before tree size N, with an STH that independent witnesses countersigned.

1. Existence = `inclusion_proof(leaf_index, hashes[])` verified against an STH whose signature and witness countersignatures check.
2. "Before date X" is provable only if the containing STH's timestamp is <= X AND the witness set for that STH was live at X.
3. Anti-backdating: the submission proxy stamps the record and rejects entries whose `issued_at` is later than log receipt (late-issuance is detectable; early-issuance is not falsifiable).

---

## 4. Disclosure tiering (I4)

Three tiers, one hash. The log entry is identical in all three cases — tier determines key distribution only, never log visibility.

| Tier | Content | Key distribution | Log entry |
|---|---|---|---|
| PUBLIC | Published openly | None needed | hash(published artifact) |
| GROUP | Ciphertext | Decryption key shared with group via E2EE channel | SHA-256(ciphertext) |
| PERSON | Ciphertext | Key sealed to one recipient | SHA-256(ciphertext) |

---

## 5. Invariants (non-negotiable properties)

- **I1 — Append-only authority.** The transparency log is the single source of truth. Entries are never modified or deleted. The Pages site, repo mirrors, and caches are derived views with no authority.
- **I2 — Existence precedes date.** No temporal claim is verifiable except via STH inclusion.
- **I3 — Ciphertext-only provenance.** The log stores SHA-256 hashes, DSSE signatures, key identifiers, and lifecycle records. Never plaintext.
- **I4 — Disclosure tiering.** Three tiers (§4), one hash. Tier determines key distribution, never log visibility.
- **I5 — Verifier independence.** Verification never trusts hub-served HTML. Verifier recomputes inclusion/consistency proofs from raw log responses.
- **I6 — Key lifecycle transparency.** Every key event is a log record. Current valid key set for any identity is derivable by replaying the log from genesis.
- **I7 — Scribe boundary.** The scribe writes hashes and signatures only. A compromised scribe loses availability, not integrity or confidentiality.
- **I8 — Separation of operators.** Hub signing key, log operator, and at least one witness operator must be independent parties/credentials.
- **I9 — No silent downgrade.** Every verdict states which trust assumptions it used (log endpoint, witness set, key state).

---

## 6. Identity and key lifecycle

Humans: OIDC (GitHub/Google) with ephemeral signing certs (Fulcio model). FACT [S3]: this is the production-proven Rekor path. FACT [S9]: OIDC Discovery is the standard for federated identity.

Agents/services: `did:web`, DID Documents hosted at `https://<org>.github.io/.well-known/did.json`, with one hardening: **the DID Document's key list is registered in the transparency log at creation, and every subsequent change is a log record (I6).** FACT [S8]: DIDs resolve to key-bearing documents without a central registry.

Bridge: SD-JWT VC (RFC 9901) when an agent must present a derived credential with selective disclosure. FACT [S5][S7]: SD-JWT + VC-DM 2.0 is the finalized selective-disclosure stack.

**Key lifecycle events (all logged):**

- **Rotation:** pre-announced windows with effective-from STH and grace period.
- **Revocation:** signed revocation record in the log, plus compact W3C Status List as a static file on Pages.
- **Loss/recovery:** pre-registered recovery set (>=2 recovery keys from different parties). Quorum-signed recovery record in the log + public dispute window (default 72h from log STH).

**ASSUMPTION:** The organization maintains one offline recovery key in cold storage. If not, recovery degrades to manual re-registration — acceptable for v1, weaker against compromised-operator scenarios.

---

## 7. Witness / monitor model

**RECOMMENDATION (resolves A-decision 2):** Minimum viable witness set = 2 + 1.

1. **Witness W1 — independent STH mirror (council-operated):** scheduled job (GitHub Action is sufficient) fetches STH, verifies consistency, appends STH chain. Failure = automated alert + kill-condition event.
2. **Witness W2 — external monitor:** `rekor-monitor` against the log configured for the hub's namespace; or a second external party's transparency watcher.
3. **The verifier's gossip check (client side):** Pages verifier and CLI compare STH against W1 mirror. Mismatch = "UNVERIFIED — STH not corroborated" verdict.

**Gate:** The hub may be described as "publicly verifiable" only once W1 and W2 have both run continuously for 30 days and the verifier implements the corroboration check. Before that: "cryptographically logged, witness coverage pending."

**OPEN — Witness operator identities:** W1 council-operated is assumed. W2 needs either `rekor-monitor` CI ownership or a second external party. Who owns W2 long-term?

---

## 8. Blockchain / distributed-ledger role

**RECOMMENDATION: Rejected for v1, in all record-level roles.**

1. The transparency-log primitive already delivers append-only, publicly auditable, third-party-verifiable ordering with inclusion proofs. [S1][S2][S3]
2. Per-record ledger writes add cost, latency, and a new trust question without removing any existing one.
3. Ledger immutability is a social property; multi-witness CT is strictly stronger per unit of trust for the hub's threat model.

**When anchoring IS justified (named exception):** If the Council needs existence proofs to survive total compromise or coercion of every witness operator, periodic anchoring of the latest STH root hash into a major public chain or an RFC 3161 timestamping authority is the correct hedge. One anchor per STH epoch (e.g., daily), never per record. **RECOMMENDATION: designed-but-unbuilt Phase 5 option behind owner gate 4.**

---

## 9. SYM-2P contract (Workstream A <-> B interface)

The narrow contract, so Workstream A ships without understanding B's internals and B evolves without breaking A:

- **Envelope:** every SYM-2P event that needs provenance is a CloudEvents v1.0 JSON envelope. FACT [S10]: `specversion, type, source, id, time, data`. SYM-2P kinds map to `com.protean.sym2p.<kind>.v1` type values.
- **Inner payload:** the existing SYM-2P/1.0 packet (wire `v: 2` unchanged). The rework adds payloads around the packet, never inside the envelope grammar.
- **To the log:** A ingests only `{ payload_hash, dsse_envelope, issuer_id, log_timestamp }`. A never sees plaintext of confidential packets (I3 at contract level).
- **Versioning:** contract version negotiated via `hub_contract` field in CloudEvents extension attributes; A rejects unknown major versions (fail-closed).
- **RECOMMENDATION:** this contract is deliberately one page. If it grows past "hash in, proof out," A and B have coupled again — treat as a design defect (kill condition K5).

---

## 10. Threat model

| Adversary | Capability | Countermeasure | Residual risk |
|---|---|---|---|
| Log operator (equivocation) | Show different trees to different clients | W1+W2 witness quorum, gossip corroboration in verifier (I5, §7) | All witnesses collude or die silently — mitigated by soak-period gate |
| Hub operator (history fraud) | Alter or backdate records | I1: log is authority; I2: dates from STHs; I8: hub key != log operator | Collusion with log operator — I8 requires independent witness |
| GitHub account compromise | Rewrite repo, swap did.json, push fake site | Repo is display-only (I1); DID swaps detected against log history (I6); verifier never trusts HTML (I5) | First-use TOFU window before DID is log-registered |
| Content sender (repudiation) | Deny having sent | DSSE signature + logged hash at send time (§6) | Sender key compromise before send — bounded by rotation policy |
| Passive observer | Read log, mirrors, Pages | I3: nothing but hashes/signatures | Traffic analysis on submission — accepted for v1 |
| Recipient (over-disclosure) | Discloses beyond authorization | Cannot be prevented post-disclosure; SD-JWT holder binding covers credential claims | Inherent to the tier model |
| Spammer | Pollute shared tenant namespace | Submission proxy rate-limit; W1 tracks hub namespace only | Proxy is liveness single point — runbook: switch endpoint to A2 |
| Key thief | Steal long-lived agent key | Short rotation windows, revocation, recovery dispute window (§7) | Theft inside grace period — accepted tradeoff |
| Scribe (compromised/failed) | Drop records, leak sessions | I7: hashes only; exclusions detectable against monitors | Availability loss until scribe restored |

---

## 11. Phased plan, gates, kill conditions

Phases are sequential within Workstream A; Workstream B runs parallel after P0.

- **P0 — Contract freeze (no code).** Lock: record schema, DSSE profile, CloudEvents type registry, DID document shape + recovery-set rules, invariants I1–I9. Exit: schemas reviewed by Frida and Mozi, owner-ratified.
- **P1 — Write path.** Submission proxy + hub namespace on public Rekor; key registration records; first real records logged. Exit: record round-trips through log with inclusion proof verified via `rekor-cli` from clean machine.
- **P2 — Read path.** Pages site + client verifier (I5); standalone CLI verifier; offline verification works (no hub HTML trust). Exit: acceptance tests T1–T4 pass.
- **P3 — Witness quorum.** W1 mirror job + W2 external monitor live; verifier corroboration check. Exit: split-view fixture detected (T5); 30-day soak begins; only after soak may copy say "publicly verifiable" (owner gate 2).
- **P4 — SYM-2P Stage 1.** 1:1 sealed-box channel + ciphertext-hash logging at send + SD-JWT disclosure flow. Exit: T6–T8 pass; validator suite still green (wire lock unbroken).
- **P5 — Conditional extensions, each behind its own owner gate:** MLS adoption (Stage 2); STH anchoring; A2 self-hosted log migration.

### Owner-held gates (council cannot cross these)

1. Log tenancy final choice (A1 start is a recommendation; A2 costs money/ops).
2. Any external/public post announcing the hub, and the "publicly verifiable" wording after P3 soak.
3. Custody ceremony for the org signing key and the offline recovery key.
4. Blockchain/timestamp-authority anchoring activation.
5. MLS (Stage 2) activation.
6. Canonical repo naming (repo names in this proposal are provisional).
7. Any legal-grade timestamp use case that would pull P5 anchoring forward.

### Kill conditions (pre-committed stop rules)

- K1: Public Rekor namespace availability degrades for >2 consecutive weeks AND A2 is unfunded -> halt A workstream, keep B.
- K2: Client verifier cannot pass offline acceptance within P2 -> do not ship "verifiable" wording; ship display-only with explicit "unverified" labels, escalate to Council.
- K3: No consumer for confidential channels materializes by end of P4 -> drop Stage 2 (MLS) permanently from roadmap; Stage 1 remains.
- K4: Witness soak shows W1 job failing unattended -> drop to single monitor + client corroboration and re-scope "publicly verifiable" claim.
- K5: Contract grows past one page / A starts parsing B's disclosure internals -> stop, re-draw the boundary.

---

## 12. Acceptance tests (T1–T10)

Verifiable, binary where possible; each names the invariant it guards.

- **T1 (I1/I5):** A record written to the log verifies via inclusion proof from a clean machine with no hub credentials, using only log API responses.
- **T2 (I5):** Pages verifier returns VERIFIED for genuine record and REJECTED for same record with one bit flipped in payload, one hash in proof path, and tampered signature — three separate negative fixtures.
- **T3 (I5):** Verifier runs fully offline given a saved (record, proof, STH, witness snapshot) bundle.
- **T4 (I2):** A record's displayed verification includes STH timestamp and tree size; altering claimed `issued_at` does not alter verified existence time.
- **T5 (I8/§8):** Split-view fixture: verifier served a fabricated STH inconsistent with W1 mirror produces UNVERIFIED — STH not corroborated verdict.
- **T6 (I3):** Property test: no log entry, mirror file, or Pages artifact contains any substring of any registered plaintext fixture — run in CI on every build.
- **T7 (I6):** After logging a revocation record, verifier rejects signatures from revoked key after grace window and still accepts during it; replaying log from genesis reproduces key state.
- **T8 (§6/I4):** Person-tier round trip: sender logs ciphertext hash; recipient reveals ciphertext; third-party verifier matches hash, verifies DSSE, confirms disclosure of SD-JWT-selected claim subset.
- **T9 (contract):** SYM-2P validator suite passes unchanged; new CloudEvents-wrapped fixtures validate; unknown `hub_contract` major version is rejected fail-closed.
- **T10 (Pages, FACT [S6]):** Site stays under Pages limits (1 GB artifact, static only); STH fetches bypass CDN caching — stale-CDN fixture does not produce false VERIFIED.

---

## 13. Unresolved decisions (open for owner + Sparky feedback)

1. **OPEN — Witness operator identities.** W2 long-term owner (uptime accountability).
2. **OPEN — Cold recovery key custody.** Confirm a party holds the offline key.
3. **OPEN — Legal-grade timestamp requirement.** If any real use case exists, P5 anchoring moves from "designed" to "scheduled."
4. **OPEN — Confidential-channel consumer list.** The Stage-2 MLS gate fires on measured need; candidate consumers named now so K3 has a concrete test.
5. **OPEN — Data retention policy.** Indefinite retention is simplest and safest for I1/I6. Owner to confirm "keep forever."
6. **OPEN — Namespace convention on public log.** Exact Rekor namespace/marker identifying hub entries — public-surface string, owner-approved at P1 exit.
7. **OPEN — Frida's disclosure UX flows** (person/group tier) — her seat; I4 constrains but does not design them.
8. **OPEN — Offline-bundle staleness window.** Proposal: STH older than 7 days renders UNVERIFIED-STALE rather than VERIFIED.
9. **OPEN — Scribe-record filter default.** Show all with badge vs. direct-only default.

---

## 14. Source attribution

All facts are sourced from 13 primary sources (IETF RFCs, W3C Recommendations, OpenID spec, CNCF spec, official vendor docs) verified HTTP 200 on 2026-09-20. See `source-ledger.json` for full details.

---

*This proposal replaces the basic message-board concept with a public verifiable provenance architecture. It is intentionally unmerged — owner review and Sparky team feedback required before any implementation proceeds.*