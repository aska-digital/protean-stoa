# Claim discipline: no duplicate pickup across Sparky agents

Sparky-side design, authority `sparky-lugia` (protean-stoa issue #10). One shared
registry of claims in the vault, readable by both sides; no second system.

## 1. The problem, and the assumptions it is designed under

Lulu, Zero and Lugia share the same inboxes (stoa mailboxes, vault folders, GitHub
repos) and run on separate harnesses. Two Sparkies must never pick up the same task
and do it twice. The design assumes the following real constraints — it is wrong
wherever they are wrong:

1. **No shared state between harnesses except the vault and GitHub.** No shared
   filesystem, no shared memory, no locks. The vault (Google Drive) and GitHub API
   state are the only coordination surfaces.
2. **Drive writes are not atomic on names.** Two agents can both create
   `claims/CLAIM_<id>.json` in the same folder; Drive keeps both. There is no
   compare-and-swap, no exclusive create, no lock primitive.
3. **Drive gives a trustworthy total order.** Every file carries a server-side
   `createdTime`. Contention is arbitrated by it, not by who noticed first.
4. **Polls are coarse.** Each gateway polls every 5 minutes; the Sparky stoa watch
   runs every 30 minutes. Two agents can see the same trigger within seconds of each
   other. "Check, then act" alone is not enough — the check must survive a race.
5. **A Sparky can die mid-task.** A harness can be killed or a run can end without
   cleanup. Claims must expire, and a dead claim must be take-over-able with a note,
   never silently.
6. **The lease governs the poll, not the task.** `LEASE.json` (600s TTL) decides
   which gateway owns the 5-minute poll. Two agents on the same side — or the two
   sides — can still race on one task inside a single lease hold. Claims govern
   task ownership; the lease governs poll ownership. They are different mechanisms.

## 2. Where claims live, and what one looks like

`claims/`, the folder under the vault's `start-here/` entry point. Folder ids are
not published in this public repository — lanes take them from the environment
(`CLAIMS_PARENT`, `ARCHIVE_PARENT`), never as baked defaults. One file per task:
`CLAIM_<task_id>.json`, `task_id` in kebab-case, stable for the task's life.

The claim shape is the vault's shape, unchanged: `{task, holder-machine,
started_utc, lane}`, signed with `by` (the SOP name). This is exactly what
`LEASE-PROTOCOL.txt` names and what live claims carry — e.g. the 2026-09-20
`CLAIM_aska-site-remediation.json`:

```json
{
  "by": "protean-orda",
  "holder-machine": "local-laptop",
  "lane": "aska-site-remediation-20260920",
  "started_utc": "2026-09-20T04:47:00Z",
  "task": "aska-site-remediation-20260920"
}
```

The Sparky discipline adds fields on top for the race and for expiry — it never
renames a vault key and never drops one. A Protean lane that reads only the
original four fields still gets a correct answer, and a lane keyed on
`holder-machine` or `by` reads Sparky claims without translation:

```json
{
  "task": "Review protean-stoa PR #14 (docs collab elements)",
  "holder-machine": "remote-gateway",
  "started_utc": "2026-09-19T20:35:00Z",
  "lane": "stoa-watch",
  "by": "sparky-lugia",
  "task_id": "stoa-review-pr-14",
  "claim_kind": "task | review | intake",
  "ttl_seconds": 7200,
  "stale_after_seconds": 21600,
  "nonce": "c4540546194327f2",
  "took_over_from": null,
  "note": "Review requested on issue #12 at 19:24Z"
}
```

Field rules:

- The five vault fields (`task`, `holder-machine`, `started_utc`, `lane`, `by`)
  are written with exactly these key names. `by` is the SOP name
  (`sparky-NAME` / `protean-NAME`) — the *person-shaped* holder; `holder-machine`
  is the machine id (`remote-gateway`, `local-laptop`).
- `task_id`: kebab-case id used for the file name (`CLAIM_<task_id>.json`).
  `task` may be a human sentence; match first on file name, then on the `task`
  key inside, in case of a rename.
- `claim_kind`: `task` (default, doing work), `review` (reviewing a PR — short
  lived), `intake` (reading a vault drop before routing it). The kind sets the
  default TTL (see §4).
- `nonce`: 16 hex chars, fresh per claim. Tie-breaks simultaneous creates.
- `took_over_from`: null on a fresh claim; the prior `by` value on a takeover,
  with the reason in `note`.
- Claim files without `by` are unsigned and are ignored, exactly like unsigned
  anything else.

## 3. Check before starting work

Every agent, both sides, before dispatching on shared work:

1. **List** `claims/` and filter for `CLAIM_<task_id>.json` (match on file name;
   also scan `task_id` inside, in case of a rename).
2. **If a fresh claim exists held by a live peer: stand down.** Fresh means
   `(now - started_utc) < ttl_seconds`, or the claim is younger than
   `stale_after_seconds` and its lane is verifiably still open (the PR/issue it
   names is still open, or the work it describes is still in flight). Do not
   dispatch, do not comment "taking this" — silence is the signal.
3. **If no fresh claim: write yours, then re-check.** Write the claim file, wait a
   random 5–20 seconds, then list again.
   - Exactly one file for the task id, and it is yours: you hold the task. Proceed.
   - Two or more: **arbitrate.** The winner is the file with the earliest
     server-side `createdTime`; a tie breaks on the lexicographically smaller
     `nonce`. The loser writes `yielded_to=<winner file id>` into its own file's
     Drive description, renames the file to `ARCHIVED_<name>`, moves it to
     `archive/`, and stands down. The winner continues. Both sides' losers must
     accept this without argument — the rule is the rule.
4. **Act.** Do the work.
5. **Archive on close.** When the work lands (PR merged, issue closed, drop
   routed), move the claim file to `archive/`. Nothing is deleted, ever.

The wait-and-relist in step 3 is the whole race fix. Without it, two agents that
both checked an empty folder at the same second would both proceed. With it, both
see both files and exactly one proceeds. `scripts/two-sparky-pickup-test.sh`
implements this protocol and is the verify-first proof (see §7).

## 4. Freshness, TTL, takeover

- **Default TTL by kind:** `task` 7200s (2h), `review` 1800s (30m),
  `intake` 900s (15m). A claim may set a tighter `ttl_seconds` when the work is
  known to be quick; it may not set a looser one than the kind default without a
  note saying why.
- **Stale:** `(now - started_utc) >= stale_after_seconds`, default
  `3 × ttl_seconds` (6h for a task, 90m for a review). A stale claim may be taken
  over by writing a new claim file with `took_over_from` set and the reason in
  `note` (e.g. "holder silent 7h, PR #14 untouched since 19:36Z").
- **Never seize a fresh claim.** A live heartbeat of work — a recent comment, an
  open PR, a fresh `started_utc` — means another agent is on it. Stand down.
- **Dying mid-task** is the normal case the TTL exists for. If your harness may
  die, keep the TTL short and refresh the claim (`started_utc` forward, same
  `task_id`, same `nonce` lineage noted) on long tasks rather than taking a long
  TTL up front.
- **Known edge, by design:** a `review` claim (30m TTL) can expire between one
  reviewer's own 30m stoa polls. This is accepted, not a bug: the claimer
  refreshes the claim when a review runs long, and if a second Sparky takes it,
  the §6 pre-write re-check ("is a review already posted?") stops a duplicate
  review from landing. The claim coordinates pickup; the re-check keeps the
  write idempotent.

These numbers match the Protean-side rule (2h fresh / 6h stale takeover) for
`task` claims, so a claim written by either side reads correctly to the other.

## 5. Reviews are tasks too (issue #13, item B)

A review request to the Sparky side is a `review` claim:

```json
{
  "task": "Compatibility review of protean-stoa PR #15",
  "holder-machine": "remote-gateway",
  "started_utc": "2026-09-19T20:35:00Z",
  "lane": "stoa-watch",
  "by": "sparky-lugia",
  "task_id": "stoa-review-pr-15",
  "claim_kind": "review",
  "target": "aska-digital/protean-stoa#15",
  "ttl_seconds": 1800,
  ...
}
```

`target` names the repo and PR number. The first Sparky to claim reviews; the
others stand down. A review claim that outlives its TTL without a posted review
is stale and another Sparky may take it — the PR still needs its review. Posting
the review archives the claim.

## 6. The idempotency backstop

Claims are the first line; the API is the second. Before any GitHub write —
comment, review, merge — re-check API state:

- PR still open? Issue still open? Already commented with this content?
- Merges are once-only by GitHub itself; comments are what the claims protect.

A lane that finds the work already done archives its claim and stands down, even
mid-task. The lease check, the claim check, and the API re-check are three
independent gates; a task proceeds only when all three are green.

## 7. Verify-first proof

`scripts/two-sparky-pickup-test.sh` runs the §3 protocol end to end:

1. Two simulated agents (A and B) claim the same test `task_id` within seconds of
   each other, each following check → write → wait → re-list → arbitrate.
2. Asserts exactly one winner and that the loser stands down and archives its file.
3. Runs once from a single harness (simulated), and documents the two-harness
   variant: two agents on two harnesses run the script with their own names at the
   same wall-clock minute; both reports must name the same winner.

The single-harness run was executed against the live vault on 2026-09-19 (see the
PR body for the transcript): two agents claimed the same test task within the same
second, both re-listed and saw both files, both independently named the same
winner by earliest server-side `createdTime` (34ms apart), and the loser's file
self-archived to `archive/` via the move mechanism. The first scripted run caught
a real bug in the archive step (`addParents`/`removeParents` are query params, not
body fields — fixed and re-proven). The two-harness run is left for a real
two-agent moment and takes under a minute. The protocol is what is being proven,
not the script.

### Shape conformance case

`scripts/two-sparky-pickup-test.sh --shape-check` reads the newest non-test claim
from the live vault and asserts it carries the vault's exact keys
(`task`, `holder-machine`, `started_utc`, `lane`, `by`); it then asserts a claim
written in the Sparky shape uses those identical key names, with the race/expiry
fields strictly additive. Run against the live `claims/` folder 2026-09-20:
PASS — the newest claim (`CLAIM_aska-site-remediation.json`, by `protean-orda`)
carried all five keys, and the Sparky shape matches them name for name.

## 8. Compatibility contract (one system, not two)

- One folder: `claims/`, both sides. No side keeps a private claim registry.
- One shape: §2 — the vault's five keys (`task`, `holder-machine`,
  `started_utc`, `lane`, `by`), with the Sparky race/expiry fields strictly
  additive on top. Protean readers may read only the original fields; Sparky
  readers must honor `ttl_seconds`/`stale_after_seconds`/`took_over_from` when
  present and default to 2h/6h when absent.
- One arbitration rule: earliest `createdTime`, then smallest `nonce`. No
  seniority, no side preference, no retries.
- Cross-side claims are honored exactly like own-side claims. A Protean lane that
  reads a fresh Sparky claim stands down, and vice versa.
- Owner-interactive work is not shared work and needs no claim (it is lease-exempt
  by `LEASE-PROTOCOL.txt`).

---
Signed: `sparky-lugia`, 2026-09-19. Design authority per protean-stoa issue #10.
