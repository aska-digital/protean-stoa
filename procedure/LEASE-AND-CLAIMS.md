# Lease and claims (dual gateway)

Two machines read the same vault and the same mailboxes, so a shared task must never be picked up twice. The vault carries two mechanisms for it, plus an idempotency backstop. The protocol of record is `LEASE-PROTOCOL.txt` under `start-here/` in the vault; this document restates it for the repository.

## The lease — who owns the poll

`LEASE.json` under `start-here/` names one holder at a time. The holder owns the 5-minute poll and all shared-work dispatch: Sparky reviews, exchange handshakes, vault routing.

- Heartbeat every tick. TTL 600 seconds.
- A lease whose heartbeat is older than the TTL is stale, and any side may take it by writing its own machine id and a fresh time.
- **Never seize a live lease.** A machine that finds a live heartbeat held by another machine stays standby until that heartbeat goes stale.
- Laptop lid closes, heartbeats stop, the remote side takes over automatically. Laptop wakes, sees a live remote heartbeat, and stays standby.
- Owner-interactive work stays local whatever the lease says. Work that needs the owner in the room is not shared work.

Machine ids are `local-laptop` and `remote-gateway`. Every take is signed with the `protean-NAME` or `sparky-NAME` on top of the machine id.

## Claims — who owns the task

`start-here/claims/` holds one file per task, named `CLAIM_<id>.json`:

```json
{"task": "<what the task is>", "holder-machine": "<machine id>", "started_utc": "<UTC>", "lane": "<lane>"}
```

- **Claim before dispatch.** Write the claim file before a lane is dispatched on shared work.
- **Skip a fresh claim.** If a claim for the same task already exists and is fresh, do not dispatch. Fresh means younger than 2 hours, or its lane still open.
- **Archive on close.** When the lane closes, the claim is moved to `start-here/archive/`. Nothing is deleted.
- **Stale takeover.** A claim older than 6 hours may be taken over, with a note written into the file.

## Backstop

Shared lanes re-check API state before acting: already merged? already commented? Merges are naturally once-only, so comments are the thing the claims protect. The lease protects poll ownership, the claims protect task ownership, and the API re-check covers what neither can.
