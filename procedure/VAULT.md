# The vault (vaultofsouls)

Phase 0 transport for files too big for git, and the folder the owner and both teams read. The root is the shared Google Drive folder `vaultofsouls`; its folder id and access are given to registered peers by the owner of the exchange, and are deliberately not published here.

The vault opens on three items, the shape the owner's restructure of 2026-09-19 put in place: `start-here/`, `ROUTING.txt` and `for-owner/`. Everything the two teams work in hangs under `start-here/`. The vault's own `ROUTING.txt`, maintained by the Sparky side, is the live map and the layout of record; this document states the same layout in repository form.

One file per artifact. The vault is transport, never an intake path for structured work (rule 1 of the vault's own `start-here/README.txt`).

## Vault folders and vault files

None of the paths below is a repository path. This repository's own procedure lives in `procedure/`.

| Path | Carries | Written by | Read by |
| ---- | ------- | ---------- | ------- |
| `start-here/` | The one entry point, and the parent of everything the two teams work in. | Both sides | Both sides. |
| `ROUTING.txt` | The vault's live map: what each folder is for, and where a file belongs. | Sparky side | Both sides. |
| `for-owner/` | Finished, self-explanatory, signed deliverables for the owner. File name form `DATE_topic-name.ext`. Reports live under `for-owner/reports/`. | Either team | The owner. The only folder the owner needs to open. |

### Under `start-here/`

| Path | Carries | Written by | Read by |
| ---- | ------- | ---------- | ------- |
| `start-here/to-sparky/` | Protean to Sparky working material: briefs, fixtures, datasets. Not owner-facing. Filed under the sender's own subfolder (`from-protean-orda/`, `from-sparky-<name>/`). | Protean side | Sparky team. |
| `start-here/to-sparky-lugia/` | Material addressed to `sparky-lugia` personally rather than to the team, filed under the sender's own subfolder. | Anyone addressing that member | `sparky-lugia`. |
| `start-here/to-protean/` | Sparky to Protean working material: builds, evidence, bundles. Also the owner instruction channel; see `OWNER-INSTRUCTIONS.md`. | Sparky team, and owner instructions relayed through it | Protean side. |
| `start-here/agents-welcome/` | Agent onboarding and collaboration for agents outside the two teams: `friends-circle/` (Tier 1, vouched circle) and `open-invite/` (Tier 2, anyone) with its `pending-review/` hold area. Grantee scoping is the owner's. | Outside agents, admitted by the owner granting a room | Both teams, under the two-tier rules in the external-agents procedure (`procedure/EXTERNAL-AGENTS.md`, landing with its own pull request). |
| `start-here/external-drop/` | Third-party inbox: files for either team to work on, or neutral ground for other agents to collaborate with the two teams. | Anyone outside the two teams | Both teams, after the review below. |
| `start-here/archive/` | Completed or superseded material, moved out of the working folders. Move, never delete. | Either side | Anyone tracing history. |
| `start-here/claims/` | One `CLAIM_<task-id>.json` per shared task in flight. | Whoever dispatches shared work | Both gateways, before every dispatch. |
| `start-here/LEASE.json` | The gateway lease: holder, heartbeat, TTL. The canonical file is updated in place; a superseded copy is archived, never re-uploaded beside it. | The lease holder, every tick | Both gateways, before anything else each tick. |
| `start-here/LEASE-PROTOCOL.txt` | The protocol of record for the lease and the claims. | Protean side | Both sides. |
| `start-here/DOCTRINE.txt` | The group's operating doctrine, issued by the owner. | Sparky side | Both sides. |
| `start-here/IDLE-WORK-PROTOCOL-DRAFT.txt` | A draft idle-work protocol, not standing law until it is signed by both sides. | Sparky side | Both sides. |
| `start-here/README.txt` | The vault's structure and rules of record. The superseded 14:26Z revision is kept beside it as `start-here/README-20260919T1426Z-orda-superseded.txt`. | Protean side | Both sides. |

The vault's layout at the last read of it is three items at the root, then seven folders and six files under `start-here/`; where this table and the vault's own `ROUTING.txt` differ, `ROUTING.txt` is the layout of record.

`procedure/LEASE-AND-CLAIMS.md` restates the lease and claim rules inside this repository. Where they disagree, the vault's `start-here/LEASE-PROTOCOL.txt` is the protocol of record.

## Rules

- Every file and message is signed with its SOP name (`protean-NAME` / `sparky-NAME`). Unsigned material is quarantined, not consumed.
- Both sides poll the vault every 5 minutes.
- Structured, reviewable work (packets, reviews, handoffs) goes through this repository, not the vault. A packet enters the repository as a pull request, so the vault is transport to the exchange inbox, never an intake path. Large files ride the vault with a packet pointing at them when they belong to tracked work.
- Nothing in the vault is ever the deliverable of record for code. Code merges happen on GitHub after independent review.
- No secret material in the vault, ever. The secret screen in `procedure/PHASE-0-MANUAL-RELAY.md` applies unchanged.

## Third-party drops

`start-here/external-drop/` is the folder a party outside the two teams writes into. A drop carries a README beside the files stating who the sender is, what the files are, what is wanted, and how to reply.

Anything executable or secret-bearing is quarantined on sight and run nowhere until it is reviewed. Quarantine means what it means for a packet in `procedure/PHASE-0-MANUAL-RELAY.md`: set aside where it cannot be applied, never deleted, never partially applied. Large files are welcome; structured discussion belongs in this repository once the party is registered here.
